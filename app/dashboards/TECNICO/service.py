import mysql.connector
from app.config import settings
from app.dashboards.TECNICO.queries import TecnicoQueries

class TecnicoService:
    def __init__(self):
        # Usamos as configurações centralizadas do seu projeto
        self.config = {
            'host': settings.DB_HOST,
            'user': settings.DB_USER,
            'password': settings.DB_PASS,
            'database': settings.DB_NAME,
            'port': settings.DB_PORT
        }

    def get_dashboard_tecnico(self, inicio, fim):
        """
        Coleta e processa todos os KPIs técnicos do banco IXC.
        """
        conn = None
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(dictionary=True)

            # 1. Busca os KPIs dos Cards (Volume, SLA, Reincidência, etc)
            cursor.execute(TecnicoQueries.get_resumo_kpis(inicio, fim))
            resumo = cursor.fetchone()

            # 2. Busca o Ranking de Técnicos (Barras Empilhadas)
            cursor.execute(TecnicoQueries.get_produtividade_tecnicos(inicio, fim))
            ranking = cursor.fetchall()

            # 3. Busca a Distribuição por Setor (Pizza/Donut)
            cursor.execute(TecnicoQueries.get_distribuicao_setor(inicio, fim))
            setores = cursor.fetchall()

            # Retornamos os dados organizados
            return {
                "resumo": resumo if resumo else {},
                "ranking": ranking if ranking else [],
                "setores": setores if setores else []
            }

        except Exception as e:
            print(f"Erro no TecnicoService: {e}")
            return {
                "resumo": {},
                "ranking": [],
                "setores": []
            }
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
