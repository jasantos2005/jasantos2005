import sqlite3
import os
from dotenv import load_dotenv

load_dotenv()

DB_PATH = os.getenv("DB_LOCAL_PATH")

def init_local_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Tabela de Usuários
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            full_name TEXT,
            is_admin BOOLEAN DEFAULT 0
        )
    ''')

    # Tabela de Dashboards (Catálogo)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dashboards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            sector TEXT NOT NULL
        )
    ''')

    # Relacionamento RBAC (Permissões)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS user_dashboards (
            user_id INTEGER,
            dashboard_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(dashboard_id) REFERENCES dashboards(id),
            PRIMARY KEY(user_id, dashboard_id)
        )
    ''')

    # Auditoria de Acesso
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS audit_access (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            dashboard_code TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            ip_address TEXT
        )
    ''')

    conn.commit()
    conn.close()

if __name__ == "__main__":
    init_local_db()
