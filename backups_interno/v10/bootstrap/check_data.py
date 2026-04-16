import mysql.connector
import os
from dotenv import load_dotenv

# Carrega credenciais do Henry (conforme definido no .env)
load_dotenv(dotenv_path="/opt/automacoes/GSG/gestao/diretoria/dashboards/app/.env")

def test_raw_query():
    print("🚀 Axiom Engine: Iniciando tentativa de conexão com ixcprovedor...")
    try:
        conn = mysql.connector.connect(
            host=os.getenv("DB_HOST"),
            user=os.getenv("DB_USER"),
            password=os.getenv("DB_PASS"),
            database=os.getenv("DB_NAME"),
            port=int(os.getenv("DB_PORT"))
        )
        if conn.is_connected():
            cursor = conn.cursor()
            # Teste de faturamento simples: Últimos 5 pagamentos registrados
            query = "SELECT id, valor_pago, data_pagamento FROM fn_receber WHERE status = 'R' ORDER BY data_pagamento DESC LIMIT 5"
            cursor.execute(query)
            rows = cursor.fetchall()
            
            print("✅ CONEXÃO ESTABELECIDA COM SUCESSO!")
            print("--------------------------------------------------")
            print("AMOSTRA DE DADOS (fn_receber):")
            for row in rows:
                print(f"ID: {row[0]} | Valor: R$ {row[1]} | Data: {row[2]}")
            print("--------------------------------------------------")
            
            cursor.close()
            conn.close()
    except Exception as e:
        print(f"❌ FALHA CRÍTICA NA CONEXÃO: {e}")

if __name__ == "__main__":
    test_raw_query()
