import mysql.connector
import os
from dotenv import load_dotenv

load_dotenv(dotenv_path="/opt/automacoes/GSG/gestao/diretoria/dashboards/app/.env")

def discover_tables():
    print("🔍 Axiom Discovery: Mapeando tabelas de financeiro no ixcprovedor...")
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT"))
        )
        cursor = conn.cursor()
        # Busca tabelas que contenham 'receber' ou 'fn' no nome
        cursor.execute("SHOW TABLES LIKE '%receber%'")
        tables = cursor.fetchall()
        
        print("✅ Tabelas encontradas:")
        for t in tables:
            print(f"-> {t[0]}")
            
        if not tables:
            print("⚠️ Nenhuma tabela com 'receber' encontrada. Listando todas as tabelas 'fn':")
            cursor.execute("SHOW TABLES LIKE 'fn%'")
            for t in cursor.fetchall(): print(f"-> {t[0]}")

        cursor.close()
        conn.close()
    except Exception as e:
        print(f"❌ Erro: {e}")

if __name__ == "__main__":
    discover_tables()
