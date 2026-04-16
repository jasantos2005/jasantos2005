import sqlite3
import os
import sys
from dotenv import load_dotenv

# Adiciona o diretório app ao path para importar security
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app.core.security import get_password_hash

load_dotenv(dotenv_path="../app/.env")
DB_PATH = os.getenv("DB_LOCAL_PATH")

def bootstrap():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # Criar Admin Padrão
    admin_user = "admin"
    admin_pw = "axiom@2026"  # Alterar no primeiro acesso
    pw_hash = get_password_hash(admin_pw)

    try:
        cursor.execute("INSERT OR IGNORE INTO users (username, password_hash, full_name, is_admin) VALUES (?, ?, ?, ?)",
                       (admin_user, pw_hash, "Administrador Axiom", 1))
        
        # Criar Dashboards de Exemplo para o Catálogo
        dashboards = [
            ('FIN_REC', 'Financeiro Receitas', 'Financeiro'),
            ('COM_VENDAS', 'Comercial Vendas', 'Comercial'),
            ('TI_INFRA', 'Infraestrutura TI', 'TI')
        ]
        cursor.executemany("INSERT OR IGNORE INTO dashboards (code, name, sector) VALUES (?, ?, ?)", dashboards)
        
        conn.commit()
        print(f"✅ Sucesso: Admin '{admin_user}' criado e dashboards catalogados.")
    except Exception as e:
        print(f"❌ Erro no bootstrap: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    bootstrap()
