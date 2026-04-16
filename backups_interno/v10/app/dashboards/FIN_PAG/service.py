import mysql.connector
from app.config import settings
import os

class PagarService:
    def __init__(self):
        self.config = {
            'host': settings.DB_HOST, 'user': settings.DB_USER,
            'password': settings.DB_PASS, 'database': settings.DB_NAME, 'port': settings.DB_PORT
        }
        self.path_sql = "/opt/automacoes/GSG/gestao/diretoria/dashboards/app/dashboards/FIN_PAG/queries.sql"

    def _execute(self, query_name, inicio="", fim=""):
        try:
            if not os.path.exists(self.path_sql):
                return {"total": 0}

            with open(self.path_sql, 'r', encoding='utf-8') as f:
                queries = f.read().split('-- @')

            sql = next((q.replace(query_name, '').strip() for q in queries if q.strip().startswith(query_name)), "")
            if not sql: return {"total": 0}

            if inicio: sql = sql.replace(':inicio', f"'{inicio}'")
            if fim: sql = sql.replace(':fim', f"'{fim}'")

            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql)
            result = cursor.fetchone()
            while cursor.nextset(): pass
            cursor.close()
            conn.close()
            return result if result else {"total": 0}
        except Exception as e:
            print(f"Erro no Service Pagar ({query_name}): {e}")
            return {"total": 0}

    def _execute_list(self, query_name, inicio="", fim=""):
        """Novo método para retornar listas de resultados (ex: Top Fornecedores)"""
        try:
            if not os.path.exists(self.path_sql): return []
            with open(self.path_sql, 'r', encoding='utf-8') as f:
                queries = f.read().split('-- @')
            
            sql = next((q.replace(query_name, '').strip() for q in queries if q.strip().startswith(query_name)), "")
            if not sql: return []

            if inicio: sql = sql.replace(':inicio', f"'{inicio}'")
            if fim: sql = sql.replace(':fim', f"'{fim}'")

            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql)
            result = cursor.fetchall() # Captura todos os registros
            cursor.close()
            conn.close()
            return result if result else []
        except Exception as e:
            print(f"Erro List Service Pagar ({query_name}): {e}")
            return []

    def get_resumo_pagar(self, inicio="", fim=""):
        return {
            "passivo_total": self._execute('QUERY_PASSIVO_TOTAL', inicio, fim),
            "passivo_vencido": self._execute('QUERY_PASSIVO_VENCIDO', inicio, fim),
            "pressao_30d": self._execute('QUERY_PRESSAO_30D', inicio, fim),
            "projecao_90d": self._execute('QUERY_PROJECAO_90D', inicio, fim),
            "sustentabilidade": self._execute('QUERY_SUSTENTABILIDADE', inicio, fim),
            "top_fornecedores": self._execute_list('QUERY_TOP_FORNECEDORES', inicio, fim)
        }
