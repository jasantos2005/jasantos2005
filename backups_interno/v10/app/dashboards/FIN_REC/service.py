import mysql.connector
from app.config import settings
import os

class FinanceiroService:
    def __init__(self):
        # Configurações vindas do seu app/config.py
        self.config = {
            'host': settings.DB_HOST,
            'user': settings.DB_USER,
            'password': settings.DB_PASS,
            'database': settings.DB_NAME,
            'port': settings.DB_PORT
        }
        # Caminho absoluto conforme o mapa do diretório
        self.path_sql = "/opt/automacoes/GSG/gestao/diretoria/dashboards/app/dashboards/FIN_REC/queries.sql"

    def _execute(self, query_name, multi=False):
        """
        Lê o arquivo .sql e extrai a query baseada na tag -- @SQL_XX
        multi=True: usa fetchall() para listas (Gráficos/Tabelas)
        multi=False: usa fetchone() para valores únicos (Cards)
        """
        try:
            if not os.path.exists(self.path_sql):
                print(f"ERRO CRÍTICO: Arquivo não encontrado em {self.path_sql}")
                return [] if multi else {}

            with open(self.path_sql, 'r', encoding='utf-8') as f:
                content = f.read()
                sections = content.split('-- @')

            sql = ""
            for section in sections:
                if section.strip().startswith(query_name):
                    sql = section.replace(query_name, '', 1).strip()
                    break

            if not sql:
                print(f"AVISO: A query {query_name} não foi encontrada dentro do arquivo SQL.")
                return [] if multi else {}

            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql)

            if multi:
                result = cursor.fetchall()
            else:
                result = cursor.fetchone()

            while cursor.nextset(): pass

            cursor.close()
            conn.close()

            if result:
                return result
            return [] if multi else {}

        except Exception as e:
            print(f"Erro na execução da {query_name}: {e}")
            return [] if multi else {}

    def get_resumo(self, inicio, fim):
        return {
            "recuperacao_mes_ant": self._execute('SQL_01'),
            "recuperacao_historica": self._execute('SQL_02'),
            "pagamento_prazo": self._execute('SQL_03'),
            "media_atraso": self._execute('SQL_04'),
            "arpu_caixa": self._execute('SQL_05'),
            "inadimplencia_mes": self._execute('SQL_06'),
            "inadimplencia_ano": self._execute('SQL_07'),
            "inadimplencia_fechada": self._execute('SQL_08'),
            "exposicao_mes": self._execute('SQL_09'),
            "exposicao_ano": self._execute('SQL_10')
        }

    def get_bi_evolucao(self):
        dados_raw = self._execute('SQL_11', multi=True)
        return {
            "labels": [row['mes'] for row in dados_raw] if dados_raw else [],
            "recebido": [float(row['recebido'] or 0) for row in dados_raw] if dados_raw else [],
            "inadimplente": [float(row['inadimplente'] or 0) for row in dados_raw] if dados_raw else []
        }

    def get_aging_data(self):
        dados_raw = self._execute('SQL_12', multi=True)
        return {
            "labels": [row['faixa'] for row in dados_raw] if dados_raw else [],
            "valores": [float(row['valor'] or 0) for row in dados_raw] if dados_raw else []
        }

    def get_top_devedores(self):
        result = self._execute('SQL_13', multi=True)
        return result if result else []

    def get_fluxo_caixa(self):
        """
        Versão 9: Busca o consolidado de Entradas vs Saídas do mês atual
        """
        result = self._execute('SQL_14', multi=False)
        if result:
            return {
                "entradas": float(result['total_entradas'] or 0),
                "saidas": float(result['total_saidas'] or 0),
                "resultado": float(result['resultado_mes'] or 0)
            }
        return {"entradas": 0, "saidas": 0, "resultado": 0}

    def get_performance_mensal(self):
        """
        Versão 10: Processa Faturamento, Recebido e Inadimplência mensal
        """
        dados_raw = self._execute('SQL_15', multi=True)
        
        if not dados_raw:
            return {"labels": [], "faturado": [], "recebido": [], "vencido": [], "perc_inad": []}

        return {
            "labels": [row['mes_ref'] for row in dados_raw],
            "faturado": [float(row['valor_faturado'] or 0) for row in dados_raw],
            "recebido": [float(row['total_recebido'] or 0) for row in dados_raw],
            "vencido": [float(row['saldo_vencido'] or 0) for row in dados_raw],
            "perc_inad": [float(row['percentual_inadimplencia'] or 0) for row in dados_raw]
        }
