#!/usr/bin/env python3
"""
cron_resumo_matinal_gsg.py — Resumo financeiro diário GSG
Envia todo dia às 08h: inadimplência + exposição de risco + comercial
"""
import os, sys, requests
from datetime import datetime, date, timedelta, timezone
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
ENV_PATH = BASE_DIR / ".env"

for line in ENV_PATH.read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

TOKEN       = os.getenv("TELEGRAM_TOKEN","")
CHAT_AILTON = os.getenv("TELEGRAM_AILTON","")
CHAT_GRUPO  = os.getenv("TELEGRAM_CHAT_ID","")

def brt():
    return (datetime.now(timezone.utc) - timedelta(hours=3))

def notificar(msg, chat):
    if not TOKEN or not chat: return
    try:
        requests.post(f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id":chat,"text":msg,"parse_mode":"HTML"}, timeout=10)
    except Exception as e:
        print(f"[TELEGRAM] {e}")

def buscar_financeiro():
    try:
        sys.path.insert(0, str(BASE_DIR.parent))
        from app.core.ixc_db_gsg import ixc_select_one, ixc_select
        hoje = date.today().strftime("%Y-%m-%d")
        mes  = date.today().replace(day=1).strftime("%Y-%m-%d")

        # Inadimplência
        r_inad = ixc_select_one("""
            SELECT COUNT(DISTINCT cc.id) as qtd,
                   SUM(f.valor_aberto) as valor
            FROM ixcprovedor.cliente_contrato cc
            JOIN ixcprovedor.fn_areceber f ON f.id_contrato=cc.id
            WHERE cc.status='A' AND cc.status_internet IN ('A','FA')
              AND f.status='A' AND f.data_vencimento < CURDATE()
        """)

        # Vencendo hoje
        r_hoje = ixc_select_one("""
            SELECT COUNT(*) as qtd, SUM(valor) as valor
            FROM ixcprovedor.fn_areceber
            WHERE status='A' AND data_vencimento=CURDATE()
        """)

        # Comercial hoje
        r_com = ixc_select_one("""
            SELECT COUNT(*) as total,
                   SUM(status_internet='A') as ativados,
                   SUM(status_internet='AA') as aguard
            FROM ixcprovedor.cliente_contrato
            WHERE data >= %s AND id_vendedor_ativ > 0 AND id_vendedor_ativ != 29
        """, (hoje,))

        # Top vendedor do mês
        r_top = ixc_select("""
            SELECT v.nome, COUNT(*) as total
            FROM ixcprovedor.cliente_contrato cc
            JOIN ixcprovedor.vendedor v ON v.id=cc.id_vendedor_ativ
            WHERE cc.data >= %s AND cc.status_internet='A'
              AND cc.id_vendedor_ativ > 0 AND cc.id_vendedor_ativ != 29
            GROUP BY v.id, v.nome ORDER BY total DESC LIMIT 1
        """, (mes,))

        return r_inad, r_hoje, r_com, r_top[0] if r_top else None
    except Exception as e:
        print(f"[FINANCEIRO] {e}")
        return None, None, None, None

def fmt_brl(v):
    try: return f"R$ {float(v or 0):,.2f}".replace(",","X").replace(".",",").replace("X",".")
    except: return "R$ 0,00"

def montar_msg():
    agora = brt()
    data_fmt = agora.strftime("%d/%m/%Y")
    r_inad, r_hoje, r_com, top_vend = buscar_financeiro()

    linhas = [
        f"☀️ <b>BOM DIA — GSG {data_fmt}</b>",
        "",
    ]

    # Financeiro
    linhas.append("💰 <b>FINANCEIRO</b>")
    if r_inad:
        qtd  = int(r_inad["qtd"] or 0)
        val  = float(r_inad["valor"] or 0)
        linhas.append(f"  • Inadimplentes ativos: <b>{qtd} clientes</b> | {fmt_brl(val)}")
    if r_hoje:
        qtd_h = int(r_hoje["qtd"] or 0)
        val_h = float(r_hoje["valor"] or 0)
        linhas.append(f"  • Vencendo hoje: <b>{qtd_h} títulos</b> | {fmt_brl(val_h)}")
    linhas.append("")

    # Comercial
    linhas.append("📊 <b>COMERCIAL — hoje</b>")
    if r_com:
        linhas.append(f"  • Leads: <b>{int(r_com['total'] or 0)}</b>")
        linhas.append(f"  • Ativados: <b>{int(r_com['ativados'] or 0)}</b>")
        linhas.append(f"  • Aguard. assinatura: <b>{int(r_com['aguard'] or 0)}</b>")
    if top_vend:
        nome = top_vend["nome"].split()[0]
        linhas.append(f"  • Líder do mês: <b>{nome}</b> ({int(top_vend['total'])} ativ.)")
    linhas.append("")
    linhas.append("💪 Bom trabalho, equipe!")

    return "\n".join(linhas)

if __name__ == "__main__":
    modo = sys.argv[1] if len(sys.argv) > 1 else "auto"
    chat = CHAT_GRUPO if "--grupo" in sys.argv else CHAT_AILTON
    msg  = montar_msg()
    if msg:
        notificar(msg, chat)
        print(f"✅ Resumo matinal enviado para {chat}")
