import mysql.connector
from mysql.connector import Error, pooling
import os
from dotenv import load_dotenv

load_dotenv()

try:
    connection_pool = mysql.connector.pooling.MySQLConnectionPool(
        pool_name="axiom_pool",
        pool_size=10,
        pool_reset_session=True,
        host=os.getenv("DB_HOST"),
        database=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        port=int(os.getenv("DB_PORT", 3306))
    )
    print("Pool de conexões MySQL Axiom estabelecido com sucesso.")
except Error as e:
    print(f"Erro ao criar pool de conexões: {e}")

def get_db_connection():
    """Retorna uma conexão do pool para consultas de negócio."""
    try:
        return connection_pool.get_connection()
    except Error as e:
        print(f"Erro ao obter conexão do pool: {e}")
        return None

def execute_query(query, params=None):
    """Executa queries de leitura e retorna dicionários."""
    conn = get_db_connection()
    if not conn:
        return []
    
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute(query, params or ())
        result = cursor.fetchall()
        return result
    except Error as e:
        print(f"Erro na execução da query Axiom: {e}")
        return []
    finally:
        cursor.close()
        conn.close()
