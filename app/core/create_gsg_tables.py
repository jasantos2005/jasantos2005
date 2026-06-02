"""
create_gsg_tables.py — Cria tabelas locais para Comercial e Estoque na GSG
"""
import sqlite3, os
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
DB_COM = str(BASE / "gsg_comercial.db")
DB_EST = str(BASE / "gsg_estoque.db")

def create_comercial():
    conn = sqlite3.connect(DB_COM)
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS gsg_vendedores (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ixc_vendedor_id INTEGER UNIQUE,
        nome TEXT NOT NULL,
        ativo INTEGER DEFAULT 1,
        criado_em TEXT DEFAULT (datetime('now','-3 hours'))
    );
    CREATE TABLE IF NOT EXISTS gsg_metas (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        vendedor_id INTEGER NOT NULL,
        mes TEXT NOT NULL,
        meta INTEGER NOT NULL DEFAULT 0,
        UNIQUE(vendedor_id, mes)
    );
    CREATE TABLE IF NOT EXISTS gsg_contratos_cache (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ixc_contrato_id INTEGER UNIQUE,
        ixc_cliente_id INTEGER,
        vendedor_id INTEGER,
        razao TEXT,
        status TEXT,
        status_internet TEXT,
        plano TEXT,
        data_contrato TEXT,
        cidade TEXT,
        sincronizado_em TEXT DEFAULT (datetime('now','-3 hours'))
    );
    CREATE INDEX IF NOT EXISTS idx_contratos_vendedor ON gsg_contratos_cache(vendedor_id);
    CREATE INDEX IF NOT EXISTS idx_contratos_data ON gsg_contratos_cache(data_contrato);
    """)
    conn.close()
    print(f"  ✅ gsg_comercial.db criado em {DB_COM}")

def create_estoque():
    conn = sqlite3.connect(DB_EST)
    conn.executescript("""
    CREATE TABLE IF NOT EXISTS gsg_produtos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ixc_produto_id INTEGER UNIQUE,
        nome TEXT NOT NULL,
        unidade TEXT DEFAULT 'un',
        tipo TEXT DEFAULT 'O',
        estoque_minimo REAL DEFAULT 0,
        ativo INTEGER DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS gsg_tecnicos_estoque (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        ixc_funcionario_id INTEGER UNIQUE,
        nome TEXT NOT NULL,
        ixc_almox_id INTEGER,
        ativo INTEGER DEFAULT 1
    );
    CREATE TABLE IF NOT EXISTS gsg_estoque_tecnico (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_tecnico INTEGER NOT NULL,
        id_produto INTEGER NOT NULL,
        quantidade REAL DEFAULT 0,
        ultima_atualizacao TEXT DEFAULT (datetime('now','-3 hours')),
        UNIQUE(id_tecnico, id_produto)
    );
    CREATE TABLE IF NOT EXISTS gsg_estoque_principal (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_produto INTEGER UNIQUE NOT NULL,
        quantidade REAL DEFAULT 0,
        ultima_atualizacao TEXT DEFAULT (datetime('now','-3 hours'))
    );
    CREATE TABLE IF NOT EXISTS gsg_requisicoes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_tecnico INTEGER NOT NULL,
        status TEXT DEFAULT 'pendente',
        obs TEXT DEFAULT '',
        emergencia INTEGER DEFAULT 0,
        aprovado_por INTEGER,
        aprovada_em TEXT,
        criada_em TEXT DEFAULT (datetime('now','-3 hours'))
    );
    CREATE TABLE IF NOT EXISTS gsg_requisicao_itens (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        id_requisicao INTEGER NOT NULL,
        id_produto INTEGER NOT NULL,
        qtd_solicitada REAL NOT NULL,
        qtd_aprovada REAL DEFAULT 0,
        obs TEXT DEFAULT ''
    );
    CREATE TABLE IF NOT EXISTS gsg_auditoria_log (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        tipo TEXT NOT NULL,
        descricao TEXT,
        divergencias INTEGER DEFAULT 0,
        criado_em TEXT DEFAULT (datetime('now','-3 hours'))
    );
    """)
    conn.close()
    print(f"  ✅ gsg_estoque.db criado em {DB_EST}")

if __name__ == "__main__":
    create_comercial()
    create_estoque()
    print("  ✅ Todas as tabelas criadas com sucesso")
