import sqlite3
import os

DB_PATH = "/opt/automacoes/GSG/gestao/diretoria/dashboards/app/gestao_local.db"

def configurar_sqlite():
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        print(f"Conectado ao SQLite em: {DB_PATH}")

        # No SQLite, 'INTEGER PRIMARY KEY' já implica em auto-incremento
        cursor.executescript("""
            CREATE TABLE IF NOT EXISTS setores (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL UNIQUE
            );

            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY,
                nome TEXT NOT NULL,
                login TEXT NOT NULL UNIQUE,
                senha_hash TEXT NOT NULL,
                id_setor INTEGER,
                status TEXT DEFAULT 'ativo'
            );

            CREATE TABLE IF NOT EXISTS permissoes_disponiveis (
                id INTEGER PRIMARY KEY,
                nome_modulo TEXT NOT NULL,
                descricao TEXT
            );

            CREATE TABLE IF NOT EXISTS usuario_permissoes (
                id_usuario INTEGER,
                id_permissao INTEGER,
                PRIMARY KEY (id_usuario, id_permissao)
            );
        """)

        # Inserir Dados
        cursor.execute("INSERT OR IGNORE INTO setores (id, nome) VALUES (1, 'GERÊNCIA'), (2, 'FINANCEIRO'), (3, 'OPERACIONAL')")
        cursor.execute("INSERT OR IGNORE INTO permissoes_disponiveis (id, nome_modulo) VALUES (1, 'FIN_REC'), (2, 'FIN_PAG')")
        
        # Senha 'admin123'
        cursor.execute("""
            INSERT OR IGNORE INTO usuarios (id, nome, login, senha_hash, id_setor) 
            VALUES (1, 'Gerente Geral', 'gerente', '240be518ebb872a617e83d17d0c3ec1818e18336110a1314d101d0ec619077a8', 1)
        """)
        
        cursor.execute("INSERT OR IGNORE INTO usuario_permissoes (id_usuario, id_permissao) VALUES (1, 1), (1, 2)")

        conn.commit()
        print("✅ AGORA SIM! Banco SQLite local pronto e populado!")
        
    except Exception as e:
        print(f"❌ Erro no SQLite: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    configurar_sqlite()
