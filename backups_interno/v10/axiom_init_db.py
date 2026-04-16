import sqlite3
import os
import bcrypt

# CONFIGURAÇÕES DE CAMINHOS
BASE_DIR = "/opt/automacoes/GSG/gestao/diretoria/dashboards/app"
CORE_DIR = os.path.join(BASE_DIR, "core")
DB_PATH = os.path.join(CORE_DIR, "axiom_auth.db")

def build_axiom():
    print("🚀 Iniciando Construção da Infraestrutura Axiom...")

    # 1. CRIAÇÃO DE DIRETÓRIOS
    dirs = [
        CORE_DIR,
        os.path.join(BASE_DIR, "auth"),
        os.path.join(BASE_DIR, "dashboards/FIN_REC"),
        os.path.join(BASE_DIR, "static"),
        os.path.join(BASE_DIR, "templates/admin")
    ]
    for d in dirs:
        if not os.path.exists(d):
            os.makedirs(d)
            print(f"✅ Pasta criada: {d}")

    # 2. RESET DO BANCO DE DADOS
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print("🧹 Banco de dados antigo removido.")

    # 3. CONEXÃO E CRIAÇÃO DE TABELAS
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    cursor.executescript('''
        CREATE TABLE users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            password_hash TEXT NOT NULL,
            is_admin BOOLEAN DEFAULT 0
        );
        CREATE TABLE dashboards (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            sector TEXT NOT NULL
        );
        CREATE TABLE user_dashboards (
            user_id INTEGER,
            dashboard_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id),
            FOREIGN KEY(dashboard_id) REFERENCES dashboards(id)
        );
    ''')
    print("📋 Tabelas de governança criadas.")

    # 4. GERAÇÃO DO USUÁRIO ADMIN (admin / admin123)
    # Usando bcrypt nativo para evitar bugs do passlib no Python 3.12
    password = "admin123".encode('utf-8')
    salt = bcrypt.gensalt(rounds=12)
    pwd_hash = bcrypt.hashpw(password, salt).decode('utf-8')

    cursor.execute("""
        INSERT INTO users (username, full_name, password_hash, is_admin) 
        VALUES (?, ?, ?, ?)
    """, ('admin', 'Administrador Axiom', pwd_hash, 1))

    # 5. CADASTRO DO DASHBOARD INICIAL
    cursor.execute("""
        INSERT INTO dashboards (code, name, sector) 
        VALUES (?, ?, ?)
    """, ('FIN_REC', 'Faturamento Recebido', 'Financeiro'))

    conn.commit()
    conn.close()
    print(f"\n✨ SUCESSO: Banco criado em {DB_PATH}")
    print("🔑 Usuário: admin | Senha: admin123")

if __name__ == "__main__":
    build_axiom()
