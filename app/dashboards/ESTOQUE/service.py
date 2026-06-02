import sqlite3, json
from pathlib import Path
from datetime import datetime, date

DB_PATH = Path("/opt/automacoes/GSG/gestao/diretoria/dashboards/app/dashboards/ESTOQUE/estoque.db")

def get_db():
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""CREATE TABLE IF NOT EXISTS produtos (
        id_produto TEXT PRIMARY KEY,
        descricao  TEXT,
        categoria  TEXT DEFAULT 'GERAL',
        unidade    TEXT DEFAULT 'un'
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS saldos (
        id_produto TEXT PRIMARY KEY,
        saldo      REAL DEFAULT 0
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS movimentacoes (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        id_produto  TEXT,
        tipo        TEXT,
        quantidade  REAL,
        responsavel TEXT,
        obs         TEXT,
        data        TEXT DEFAULT (datetime('now','-3 hours'))
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS pedidos_compra (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        itens      TEXT,
        status     TEXT DEFAULT 'pendente',
        criado_por TEXT,
        criado_em  TEXT DEFAULT (datetime('now','-3 hours'))
    )""")
    cur.execute("""CREATE TABLE IF NOT EXISTS historico_compras (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        id_produto  TEXT,
        descricao   TEXT,
        quantidade  REAL,
        fornecedor  TEXT,
        valor_total REAL DEFAULT 0,
        data        TEXT DEFAULT (datetime('now','-3 hours'))
    )""")
    conn.commit()
    conn.close()

def calcular_dias(saldo, consumo_dia):
    if not consumo_dia or consumo_dia <= 0:
        return 999
    return int(saldo / consumo_dia)

def get_itens(categoria_like, de, ate):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        SELECT p.id_produto, p.descricao, p.categoria, p.unidade,
               COALESCE(s.saldo,0) as saldo,
               COALESCE(m.saida_periodo,0) as saida_periodo
        FROM produtos p
        LEFT JOIN saldos s ON s.id_produto = p.id_produto
        LEFT JOIN (
            SELECT id_produto, SUM(quantidade) as saida_periodo
            FROM movimentacoes
            WHERE tipo='saida'
              AND (? = '' OR data >= ?)
              AND (? = '' OR data <= ?)
            GROUP BY id_produto
        ) m ON m.id_produto = p.id_produto
        WHERE p.categoria LIKE ?
        ORDER BY p.descricao
    """, (de, de, ate, ate, categoria_like))
    rows = cur.fetchall()
    conn.close()
    result = []
    for r in rows:
        if float(r["saldo"]) <= 0:
            continue
        consumo_dia = float(r["saida_periodo"]) / 30 if r["saida_periodo"] else 0
        dias = calcular_dias(float(r["saldo"]), consumo_dia)
        result.append({
            "id_produto":     r["id_produto"],
            "descricao":      r["descricao"],
            "categoria":      r["categoria"],
            "unidade":        r["unidade"],
            "saldo":          round(float(r["saldo"]), 2),
            "saida_periodo":  round(float(r["saida_periodo"]), 2),
            "consumo_dia":    round(consumo_dia, 2),
            "dias_cobertura": dias,
        })
    return result

def get_dashboard(de, ate):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        SELECT p.id_produto, p.descricao, p.categoria, p.unidade,
               COALESCE(s.saldo,0) as saldo,
               COALESCE(m.saida_periodo,0) as saida_periodo
        FROM produtos p
        LEFT JOIN saldos s ON s.id_produto = p.id_produto
        LEFT JOIN (
            SELECT id_produto, SUM(quantidade) as saida_periodo
            FROM movimentacoes
            WHERE tipo='saida'
              AND (? = '' OR data >= ?)
              AND (? = '' OR data <= ?)
            GROUP BY id_produto
        ) m ON m.id_produto = p.id_produto
    """, (de, de, ate, ate))
    rows = cur.fetchall()
    cur.execute("SELECT COUNT(*) as c FROM pedidos_compra WHERE status='pendente'")
    ped = cur.fetchone()
    pedidos_pendentes = ped["c"] if ped else 0
    conn.close()

    itens_criticos = []
    top_consumo    = []
    dias_casa = []; dias_infra = []
    total_casa = total_infra = 0

    for r in rows:
        if float(r["saldo"]) <= 0:
            continue
        consumo_dia = float(r["saida_periodo"]) / 30 if r["saida_periodo"] else 0
        dias = calcular_dias(float(r["saldo"]), consumo_dia)
        cat  = (r["categoria"] or "GERAL").upper()

        if cat == "CASA":
            total_casa += 1
            if dias < 999: dias_casa.append(dias)
        elif cat == "INFRA":
            total_infra += 1
            if dias < 999: dias_infra.append(dias)

        if dias < 20:
            itens_criticos.append({
                "id_produto":     r["id_produto"],
                "descricao":      r["descricao"],
                "categoria":      cat,
                "unidade":        r["unidade"],
                "saldo":          round(float(r["saldo"]), 2),
                "saida_periodo":  round(float(r["saida_periodo"]), 2),
                "consumo_dia":    round(consumo_dia, 2),
                "dias_cobertura": dias,
            })

        if float(r["saida_periodo"]) > 0:
            top_consumo.append({
                "id_produto":    r["id_produto"],
                "descricao":     r["descricao"],
                "unidade":       r["unidade"],
                "saida_periodo": round(float(r["saida_periodo"]), 2),
            })

    top_consumo    = sorted(top_consumo, key=lambda x: x["saida_periodo"], reverse=True)[:10]
    itens_criticos = sorted(itens_criticos, key=lambda x: x["dias_cobertura"])

    cob_casa  = int(sum(dias_casa)  / len(dias_casa))  if dias_casa  else 0
    cob_infra = int(sum(dias_infra) / len(dias_infra)) if dias_infra else 0
    rup_casa  = round(len([d for d in dias_casa  if d < 5]) / max(len(dias_casa),  1) * 100)
    rup_infra = round(len([d for d in dias_infra if d < 5]) / max(len(dias_infra), 1) * 100)

    return {
        "resumo": {
            "cobertura_casa":    cob_casa,
            "cobertura_infra":   cob_infra,
            "ruptura_pct_casa":  rup_casa,
            "ruptura_pct_infra": rup_infra,
            "itens_criticos":    itens_criticos,
            "pedidos_pendentes": pedidos_pendentes,
            "total_produtos":    len(rows),
            "total_casa":        total_casa,
            "total_infra":       total_infra,
            "top_consumo":       top_consumo,
        }
    }

def get_sugestao(de, ate):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        SELECT p.id_produto, p.descricao, p.categoria, p.unidade,
               COALESCE(s.saldo,0) as saldo,
               COALESCE(m.saida_periodo,0) as saida_periodo
        FROM produtos p
        LEFT JOIN saldos s ON s.id_produto = p.id_produto
        INNER JOIN (
            SELECT id_produto, SUM(quantidade) as saida_periodo
            FROM movimentacoes WHERE tipo='saida'
            GROUP BY id_produto
        ) m ON m.id_produto = p.id_produto
        WHERE m.saida_periodo > 0
    """)
    rows = cur.fetchall()
    conn.close()
    result = []
    for r in rows:
        if float(r["saldo"]) < 0:
            continue
        consumo_dia = float(r["saida_periodo"]) / 30 if r["saida_periodo"] else 0
        dias = calcular_dias(float(r["saldo"]), consumo_dia)
        if dias < 20:
            qtd_sugerida = max(20, int(consumo_dia * 30 * 2 - float(r["saldo"])))
            result.append({
                "id_produto":     r["id_produto"],
                "descricao":      r["descricao"],
                "categoria":      r["categoria"],
                "unidade":        r["unidade"],
                "saldo":          round(float(r["saldo"]), 2),
                "consumo_dia":    round(consumo_dia, 2),
                "dias_cobertura": dias,
                "qtd_sugerida":   qtd_sugerida,
            })
    return sorted(result, key=lambda x: x["dias_cobertura"])

def get_movimentacoes(de, ate):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        SELECT m.id, m.id_produto, p.descricao, m.tipo, m.quantidade,
               m.responsavel, m.obs, m.data
        FROM movimentacoes m
        LEFT JOIN produtos p ON p.id_produto = m.id_produto
        WHERE (? = '' OR m.data >= ?)
          AND (? = '' OR m.data <= ?)
        ORDER BY m.id DESC LIMIT 200
    """, (de, de, ate, ate))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

def registrar_movimentacao(body):
    conn = get_db()
    cur  = conn.cursor()
    agora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    cur.execute("""
        INSERT INTO movimentacoes (id_produto, tipo, quantidade, responsavel, obs, data)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (body["id_produto"], body["tipo"], body["quantidade"],
          body.get("responsavel", "manual"), body.get("obs", ""), agora))
    if body["tipo"] == "entrada":
        cur.execute("""INSERT INTO saldos (id_produto,saldo) VALUES (?,?)
            ON CONFLICT(id_produto) DO UPDATE SET saldo=saldo+?""",
            (body["id_produto"], body["quantidade"], body["quantidade"]))
    elif body["tipo"] == "saida":
        cur.execute("UPDATE saldos SET saldo=MAX(0,saldo-?) WHERE id_produto=?",
            (body["quantidade"], body["id_produto"]))
    conn.commit()
    conn.close()
    return True

def get_pedidos():
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM pedidos_compra ORDER BY criado_em DESC LIMIT 50")
    rows = cur.fetchall()
    conn.close()
    result = []
    for r in rows:
        itens = json.loads(r["itens"] or "[]")
        result.append({
            "id": r["id"], "status": r["status"],
            "qtd_itens": len(itens),
            "criado_por": r["criado_por"],
            "criado_em":  r["criado_em"],
        })
    return result

def criar_pedido(itens, criado_por):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("INSERT INTO pedidos_compra (itens,criado_por) VALUES (?,?)",
        (json.dumps(itens), criado_por))
    conn.commit()
    pid = cur.lastrowid
    conn.close()
    return pid

def get_historico(de, ate):
    conn = get_db()
    cur  = conn.cursor()
    cur.execute("""
        SELECT * FROM historico_compras
        WHERE (? = '' OR data >= ?)
          AND (? = '' OR data <= ?)
        ORDER BY data DESC LIMIT 100
    """, (de, de, ate, ate))
    rows = cur.fetchall()
    conn.close()
    return [dict(r) for r in rows]

init_db()
