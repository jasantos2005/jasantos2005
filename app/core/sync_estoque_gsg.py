#!/usr/bin/env python3
"""
sync_estoque_gsg.py — Sync IXC GSG → gsg_estoque.db
"""
import sys, os, sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent.parent
DB_PATH  = BASE_DIR / "gsg_estoque.db"
ENV_PATH = BASE_DIR / ".env"

for line in ENV_PATH.read_text().splitlines():
    line = line.strip()
    if line and not line.startswith("#") and "=" in line:
        k, v = line.split("=", 1)
        os.environ.setdefault(k.strip(), v.strip())

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

def local_conn():
    conn = sqlite3.connect(str(DB_PATH), timeout=30)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    return conn

def init_db():
    conn = local_conn()
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS produtos (
        id_produto     TEXT PRIMARY KEY,
        descricao      TEXT NOT NULL,
        categoria      TEXT DEFAULT 'GERAL',
        unidade        TEXT DEFAULT 'un',
        estoque_minimo REAL DEFAULT 0,
        ativo          INTEGER DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS saldos (
        id_produto TEXT PRIMARY KEY,
        saldo      REAL DEFAULT 0
    );
    CREATE TABLE IF NOT EXISTS movimentacoes (
        id          INTEGER PRIMARY KEY AUTOINCREMENT,
        id_produto  TEXT NOT NULL,
        tipo        TEXT NOT NULL,
        quantidade  REAL NOT NULL,
        responsavel TEXT DEFAULT 'sync',
        obs         TEXT DEFAULT '',
        data        TEXT DEFAULT (datetime('now','-3 hours'))
    );
    CREATE TABLE IF NOT EXISTS consumo_por_ativacao (
        id_produto   TEXT PRIMARY KEY,
        total_saida  REAL DEFAULT 0,
        qtd_os       INTEGER DEFAULT 0,
        media_por_os REAL DEFAULT 0,
        id_assunto   INTEGER DEFAULT 227,
        atualizado   TEXT DEFAULT (datetime('now','-3 hours'))
    );
    CREATE TABLE IF NOT EXISTS pedidos_compra (
        id         INTEGER PRIMARY KEY AUTOINCREMENT,
        itens      TEXT NOT NULL,
        status     TEXT DEFAULT 'pendente',
        criado_por TEXT DEFAULT 'master',
        criado_em  TEXT DEFAULT (datetime('now','-3 hours'))
    );
    CREATE INDEX IF NOT EXISTS idx_mov_produto ON movimentacoes(id_produto);
    CREATE INDEX IF NOT EXISTS idx_mov_data    ON movimentacoes(data);
    """)
    conn.close()

UNIDADE_MAP = {1:"un",2:"cx",3:"pct",4:"kg",5:"l",6:"m",7:"rl",8:"m",13:"un",14:"rl"}
def unidade_str(id_un):
    return UNIDADE_MAP.get(int(id_un or 1), "un")

PALAVRAS_CASA = [
    "drop","onu","roteador","router","conector","patch cord","patch-cord",
    "cordao","cordão","splitter","roseta","cpe","ont ","wifi","wi-fi","indoor",
    "residencial","adaptador","cord sc","acoplador","esticador","arame",
]
PALAVRAS_INFRA = [
    "poste","fibra","cto","ceo","caixa de emenda","caixa emenda",
    "abracadeira","abraçadeira","duto","conduite","cabo optico","cabo óptico",
    "cabo de fibra","tubete","calha","rack","dgo","dio","cabo utp","cabo ftp","cabo drop",
]

def inferir_categoria(descricao):
    d = descricao.lower()
    for p in PALAVRAS_CASA:
        if p in d: return "CASA"
    for p in PALAVRAS_INFRA:
        if p in d: return "INFRA"
    return "GERAL"

def sync_completo():
    agora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    print(f"\n🔄 Sync GSG [{agora}]")
    init_db()

    print("  [1/3] Buscando produtos do IXC...")
    conn_ixc = ixc_conn()
    cur = conn_ixc.cursor()

    # Usando colunas corretas da view estoque_produtos_almox_filial
    cur.execute("""
        SELECT id_produto,
               produto_descricao AS descricao,
               produto_unidade   AS id_unidade,
               SUM(saldo)        AS saldo_total
        FROM ixcprovedor.estoque_produtos_almox_filial
        WHERE id_almox = 1
          AND produto_ativo = 'S'
          AND produto_controla_estoque = 'S'
        GROUP BY id_produto, produto_descricao, produto_unidade
        HAVING saldo_total >= 0
        ORDER BY produto_descricao
    """)
    produtos = cur.fetchall()

    print("  [2/3] Buscando movimentações (90 dias)...")
    cur.execute("""
        SELECT mp.id_produto,
               SUM(mp.qtde_saida) AS total_saida,
               MAX(mp.data)       AS ultima_data
        FROM ixcprovedor.movimento_produtos mp
        WHERE mp.tipo = 'S'
          AND mp.id_almox = 1
          AND mp.data >= DATE_SUB(NOW(), INTERVAL 90 DAY)
          AND mp.qtde_saida > 0
        GROUP BY mp.id_produto
    """)
    movimentos = cur.fetchall()
    conn_ixc.close()

    print(f"  -> {len(produtos)} produtos | {len(movimentos)} com movimentação")

    print("  [3/3] Gravando no SQLite...")
    conn = local_conn()
    c = conn.cursor()

    for r in produtos:
        pid  = str(r["id_produto"])
        desc = (r["descricao"] or "").strip()
        un   = unidade_str(r["id_unidade"])
        cat  = inferir_categoria(desc)
        sal  = float(r["saldo_total"])
        c.execute("""
            INSERT INTO produtos(id_produto, descricao, categoria, unidade)
            VALUES(?,?,?,?)
            ON CONFLICT(id_produto) DO UPDATE SET
                descricao=excluded.descricao,
                categoria=excluded.categoria,
                unidade=excluded.unidade
        """, (pid, desc, cat, un))
        c.execute("""
            INSERT INTO saldos(id_produto, saldo) VALUES(?,?)
            ON CONFLICT(id_produto) DO UPDATE SET saldo=excluded.saldo
        """, (pid, sal))

    mov_map = {str(r["id_produto"]): float(r["total_saida"]) for r in movimentos}
    for pid, total in mov_map.items():
        if not c.execute("SELECT id_produto FROM produtos WHERE id_produto=?", (pid,)).fetchone():
            continue
        c.execute("DELETE FROM movimentacoes WHERE id_produto=? AND responsavel='sync_ixc'", (pid,))
        c.execute("""
            INSERT INTO movimentacoes(id_produto, tipo, quantidade, responsavel, obs, data)
            VALUES(?,?,?,?,?,?)
        """, (pid, "saida", total, "sync_ixc", "Saida IXC 90d",
              datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        consumo_dia = total / 90
        c.execute("""
            INSERT INTO consumo_por_ativacao(id_produto, total_saida, qtd_os, media_por_os, atualizado)
            VALUES(?,?,?,?,?)
            ON CONFLICT(id_produto) DO UPDATE SET
                total_saida=excluded.total_saida,
                atualizado=excluded.atualizado
        """, (pid, total, 0, consumo_dia, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    conn.commit()
    conn.close()
    print(f"  ✅ Sync concluído [{datetime.now().strftime('%d/%m/%Y %H:%M:%S')}]")
    return len(produtos)

if __name__ == "__main__":
    n = sync_completo()
    print(f"\n✅ {n} produtos sincronizados\n")
