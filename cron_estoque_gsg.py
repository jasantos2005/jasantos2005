#!/usr/bin/env python3
"""
cron_estoque_gsg.py — Automação de estoque GSG
- Verifica produtos em ruptura/críticos
- Envia alerta no Telegram (separado por CASA e INFRA)
- Gera pedido de compra automático no IXC (status não liberado)
- Proteção: não gera novo pedido se já existe um pendente/não liberado
"""
import os, sys, sqlite3, json, logging
from datetime import datetime, timezone, timedelta
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DB_EST   = str(BASE_DIR / "gsg_estoque.db")
ENV_PATH = BASE_DIR / ".env"

# Carregar .env
for line in ENV_PATH.read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

TOKEN        = os.getenv("TELEGRAM_TOKEN", "")
CHAT_AILTON  = os.getenv("TELEGRAM_AILTON", "")
CHAT_GRUPO   = os.getenv("TELEGRAM_CHAT_ID", "")

# Limites de cobertura para alertas
DIAS_CRITICO = 10   # menos de 10 dias → CRÍTICO
DIAS_ALERTA  = 20   # menos de 20 dias → ALERTA
DIAS_PEDIDO  = 15   # abaixo de 15 dias → gera pedido automático

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
log = logging.getLogger(__name__)

def brt():
    return (datetime.now(timezone.utc) - timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")

def notificar(msg, chat=None):
    if not TOKEN or not chat:
        return
    try:
        import requests
        r = requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": chat, "text": msg, "parse_mode": "HTML"},
            timeout=10
        )
        if not r.json().get("ok"):
            log.warning(f"Telegram erro: {r.text[:200]}")
    except Exception as e:
        log.error(f"Telegram: {e}")

def db():
    c = sqlite3.connect(DB_EST, timeout=30)
    c.row_factory = sqlite3.Row
    return c

def ixc_conn():
    import pymysql
    from pymysql.cursors import DictCursor
    conn = pymysql.connect(
        host=os.getenv("DB_HOST"), port=int(os.getenv("DB_PORT", 3306)),
        user=os.getenv("DB_USER"), password=os.getenv("DB_PASS"),
        database=os.getenv("DB_NAME"), charset="utf8mb4",
        cursorclass=DictCursor, connect_timeout=10
    )
    conn.cursor().execute("SET SESSION time_zone = '-03:00'")
    return conn

def calcular_dias(saldo, consumo_dia):
    if not consumo_dia or consumo_dia <= 0:
        return 999
    return int(saldo / consumo_dia)

def buscar_produtos_alerta():
    """Retorna produtos críticos e em alerta separados por categoria."""
    conn = db()
    rows = conn.execute("""
        SELECT p.id_produto, p.descricao, p.categoria, p.unidade,
               COALESCE(s.saldo, 0) as saldo,
               COALESCE(m.total_saida, 0) as saida_90d
        FROM produtos p
        LEFT JOIN saldos s ON s.id_produto = p.id_produto
        LEFT JOIN consumo_por_ativacao m ON m.id_produto = p.id_produto
        WHERE p.ativo = 1 AND p.categoria IN ('CASA', 'INFRA')
        ORDER BY p.categoria, p.descricao
    """).fetchall()
    conn.close()

    criticos = {"CASA": [], "INFRA": []}
    alerta   = {"CASA": [], "INFRA": []}

    for r in rows:
        saldo   = float(r["saldo"])
        saida   = float(r["saida_90d"])
        consumo = saida / 90 if saida > 0 else 0
        dias    = calcular_dias(saldo, consumo)
        qtd_sug = max(20, int(consumo * 30 * 2 - saldo)) if consumo > 0 else 0
        cat     = r["categoria"]

        item = {
            "id_produto":  r["id_produto"],
            "descricao":   r["descricao"],
            "unidade":     r["unidade"] or "un",
            "saldo":       round(saldo, 2),
            "consumo_dia": round(consumo, 2),
            "dias":        dias,
            "qtd_sugerida": qtd_sug,
        }

        if saldo <= 0 or dias < DIAS_CRITICO:
            criticos[cat].append(item)
        elif dias < DIAS_ALERTA:
            alerta[cat].append(item)

    return criticos, alerta

def ja_tem_pedido_pendente():
    """Verifica se já existe pedido automático não liberado no IXC."""
    try:
        conn = ixc_conn()
        cur  = conn.cursor()
        cur.execute("""
            SELECT COUNT(*) as total
            FROM ixcprovedor.pedido_compra
            WHERE obs LIKE '%HubEstoque GSG - Automático%'
              AND status = 'A'
              AND status_liberado = 'N'
              AND data >= DATE_SUB(NOW(), INTERVAL 7 DAY)
        """)
        r = cur.fetchone()
        conn.close()
        return (r["total"] or 0) > 0
    except Exception as e:
        log.error(f"Verificar pedido pendente: {e}")
        return False

def buscar_fornecedor_padrao():
    """Busca o fornecedor padrão (primeiro ativo) e condição de pagamento."""
    try:
        conn = ixc_conn()
        cur  = conn.cursor()
        cur.execute("SELECT id, COALESCE(fantasia, razao) as nome FROM ixcprovedor.fornecedor WHERE ativo='S' ORDER BY id LIMIT 1")
        forn = cur.fetchone()
        cur.execute("SELECT id, nome FROM ixcprovedor.condicoes_pagamento WHERE ativo='S' AND compra_venda IN ('A','C') ORDER BY id LIMIT 1")
        cond = cur.fetchone()
        conn.close()
        return forn, cond
    except Exception as e:
        log.error(f"Buscar fornecedor: {e}")
        return None, None

def buscar_ultimo_preco(cur_ixc, id_produto):
    try:
        cur_ixc.execute("""
            SELECT COALESCE(NULLIF(custo,0), valor_unitario, 0) as preco
            FROM ixcprovedor.movimento_produtos
            WHERE id_produto = %s
              AND COALESCE(NULLIF(custo,0), valor_unitario, 0) > 0
            ORDER BY data DESC LIMIT 1
        """, (id_produto,))
        r = cur_ixc.fetchone()
        return float(r["preco"]) if r else 0.0
    except:
        return 0.0

def gerar_pedido_automatico(itens_para_comprar, forn_id, cond_id, forn_nome):
    """Cria pedido no IXC com status não liberado."""
    if not itens_para_comprar:
        return None, "Sem itens para comprar"

    hoje = datetime.now().strftime("%Y-%m-%d")
    obs  = f"HubEstoque GSG - Automático - {datetime.now().strftime('%d/%m/%Y %H:%M')}"

    try:
        conn_ixc = ixc_conn()
        cur      = conn_ixc.cursor()

        # Criar pedido com status_liberado = 'N' (não liberado — aguarda aprovação)
        cur.execute("""
            INSERT INTO ixcprovedor.pedido_compra
                (data, id_fornecedor, id_condicoes_pagamento,
                 previsao_faturamento, previsao_entrega,
                 status, filial_id, id_modelo, valor_negociado,
                 obs, status_liberado, tipo_frete, valor_frete,
                 tipo_desconto, valor_desconto)
            VALUES (%s, %s, %s, %s, %s,
                    'A', 1, 1, 0,
                    %s, 'N', 'S', 0, 'V', 0)
        """, (hoje, forn_id, cond_id, hoje, hoje, obs))
        conn_ixc.commit()

        cur.execute("SELECT MAX(id) as id FROM ixcprovedor.pedido_compra")
        ixc_id = cur.fetchone()["id"]

        valor_total = 0
        itens_ok = []
        for it in itens_para_comprar:
            preco = buscar_ultimo_preco(cur, int(it["id_produto"]))
            qtd   = it["qtd_sugerida"]
            vt    = round(preco * qtd, 2)
            valor_total += vt
            cur.execute("""
                INSERT INTO ixcprovedor.pedido_compra_itens
                    (id_produto, id_unidade, quantidade, valor_unitario,
                     valor_total, id_pedido_compra, status, tipo,
                     filial_id, unidade_sigla, observacao)
                VALUES (%s, 1, %s, %s, %s, %s, 'A', 'E', 1, %s, '')
            """, (int(it["id_produto"]), qtd, preco, vt, ixc_id, it["unidade"]))
            itens_ok.append({**it, "preco": preco, "valor_total": vt})

        conn_ixc.commit()
        conn_ixc.close()

        # Salvar no banco local
        conn_local = db()
        conn_local.execute("""
            INSERT INTO pedidos_compra(itens, status, criado_por, criado_em)
            VALUES(?, 'auto_ixc', 'cron_auto', ?)
        """, (json.dumps([i["id_produto"] for i in itens_ok]), brt()))
        conn_local.commit()
        conn_local.close()

        return ixc_id, valor_total, itens_ok

    except Exception as e:
        log.error(f"Gerar pedido IXC: {e}")
        return None, str(e)

def msg_alerta(criticos, alerta, pedido_gerado=None):
    """Monta mensagem de alerta para Telegram."""
    agora = datetime.now().strftime("%d/%m/%Y %H:%M")
    total_crit = sum(len(v) for v in criticos.values())
    total_alert = sum(len(v) for v in alerta.values())

    if total_crit == 0 and total_alert == 0:
        return None

    linhas = [
        f"📦 <b>ALERTA ESTOQUE GSG — {agora}</b>",
        ""
    ]

    for cat in ["CASA", "INFRA"]:
        emoji = "🏠" if cat == "CASA" else "⚙️"
        crit  = criticos.get(cat, [])
        ale   = alerta.get(cat, [])

        if not crit and not ale:
            continue

        linhas.append(f"{emoji} <b>ESTOQUE {cat}</b>")

        if crit:
            linhas.append(f"🔴 <b>CRÍTICOS ({len(crit)}) — menos de {DIAS_CRITICO} dias:</b>")
            for i in crit[:8]:
                dias_txt = "ZERADO" if i["saldo"] <= 0 else f"{i['dias']}d"
                linhas.append(f"  • {i['descricao'][:45]}")
                linhas.append(f"    Saldo: {i['saldo']} {i['unidade']} | Cobertura: {dias_txt} | Sugerir: {i['qtd_sugerida']}")
            if len(crit) > 8:
                linhas.append(f"  ... e mais {len(crit)-8} itens críticos")

        if ale:
            linhas.append(f"🟡 <b>ALERTA ({len(ale)}) — menos de {DIAS_ALERTA} dias:</b>")
            for i in ale[:5]:
                linhas.append(f"  • {i['descricao'][:45]} — {i['dias']}d | Sugerir: {i['qtd_sugerida']} {i['unidade']}")
            if len(ale) > 5:
                linhas.append(f"  ... e mais {len(ale)-5} itens em alerta")

        linhas.append("")

    if pedido_gerado and isinstance(pedido_gerado, tuple) and pedido_gerado[0]:
        ixc_id, valor_total, itens = pedido_gerado
        linhas += [
            f"🛒 <b>PEDIDO AUTOMÁTICO GERADO</b>",
            f"📋 Pedido <b>#{ixc_id}</b> criado no IXC",
            f"⏳ Status: <b>Não Liberado</b> — aguarda aprovação do diretor",
            f"📦 {len(itens)} itens | R$ {valor_total:.2f}",
            "",
            "✅ Acesse o IXC para aprovar o pedido",
        ]
    elif pedido_gerado == "ja_existe":
        linhas += [
            "ℹ️ <b>Pedido automático não gerado</b>",
            "Já existe um pedido automático pendente de aprovação nos últimos 7 dias.",
        ]

    return "\n".join(linhas)

def rodar(modo="auto", gerar_pedido=True, chat_destino=None):
    """Função principal."""
    log.info(f"Iniciando cron_estoque_gsg [{modo}]")

    # Sync saldos primeiro
    try:
        sys.path.insert(0, str(BASE_DIR.parent))
        exec(open(str(BASE_DIR / "core" / "sync_estoque_gsg.py")).read())
    except Exception as e:
        log.warning(f"Sync falhou (continuando): {e}")

    criticos, alerta = buscar_produtos_alerta()
    total_crit  = sum(len(v) for v in criticos.values())
    total_alert = sum(len(v) for v in alerta.values())

    log.info(f"Críticos: {total_crit} | Alerta: {total_alert}")

    if total_crit == 0 and total_alert == 0:
        log.info("Estoque OK — sem alertas")
        return

    pedido_info = None

    # Gerar pedido automático apenas se tiver itens críticos
    if gerar_pedido and total_crit > 0:
        if ja_tem_pedido_pendente():
            log.info("Já existe pedido pendente — não gerando novo")
            pedido_info = "ja_existe"
        else:
            # Juntar todos os críticos de CASA e INFRA
            itens_comprar = []
            for cat in ["CASA", "INFRA"]:
                for it in criticos[cat]:
                    if it["qtd_sugerida"] > 0:
                        itens_comprar.append(it)

            if itens_comprar:
                forn, cond = buscar_fornecedor_padrao()
                if forn and cond:
                    log.info(f"Gerando pedido automático com {len(itens_comprar)} itens...")
                    resultado = gerar_pedido_automatico(
                        itens_comprar, forn["id"], cond["id"], forn["nome"]
                    )
                    pedido_info = resultado
                    if resultado[0]:
                        log.info(f"Pedido #{resultado[0]} criado no IXC")
                else:
                    log.warning("Fornecedor ou condição não encontrados")

    # Montar e enviar mensagem
    msg = msg_alerta(criticos, alerta, pedido_info)
    if msg:
        destino = chat_destino or CHAT_AILTON
        notificar(msg, destino)
        log.info(f"Alerta enviado para {destino}")

if __name__ == "__main__":
    modo         = sys.argv[1] if len(sys.argv) > 1 else "auto"
    gerar_pedido = "--sem-pedido" not in sys.argv
    chat_grupo   = "--grupo" in sys.argv

    destino = CHAT_GRUPO if chat_grupo else CHAT_AILTON

    if modo == "teste":
        # Teste sem gerar pedido
        rodar(modo="teste", gerar_pedido=False, chat_destino=CHAT_AILTON)
    elif modo == "alerta":
        # Só alerta, sem pedido
        rodar(modo="alerta", gerar_pedido=False, chat_destino=destino)
    elif modo == "pedido":
        # Alerta + pedido automático
        rodar(modo="pedido", gerar_pedido=True, chat_destino=destino)
    else:
        # Auto — decide pelo horário
        hora = datetime.now().hour
        # 08h e 14h → alerta
        # 08h segunda-feira → gera pedido automático
        dia_semana = datetime.now().weekday()  # 0=segunda
        gerar = (hora == 8 and dia_semana == 0)  # só segunda de manhã
        rodar(modo="auto", gerar_pedido=gerar, chat_destino=CHAT_AILTON)
