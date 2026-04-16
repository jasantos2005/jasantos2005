import mysql.connector
from app.config import settings
from app.dashboards.COMERCIAL.queries import ComercialQueries

class ComercialService:
    def __init__(self):
        # Configuração de conexão centralizada no settings
        self.config = {
            'host': settings.DB_HOST,
            'user': settings.DB_USER,
            'password': settings.DB_PASS,
            'database': settings.DB_NAME,
            'port': settings.DB_PORT
        }

    def get_dashboard_comercial(self, inicio, fim, vendedor_id=None):
        """
        Consolida os dados comerciais. 
        Agora aceita vendedor_id para filtrar os resultados.
        """
        conn = None
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(dictionary=True)

            # 1. Busca Resumo Executivo (Cards) - Passando vendedor_id
            cursor.execute(ComercialQueries.get_resumo_geral(inicio, fim, vendedor_id))
            resumo = cursor.fetchone()

            # 2. Busca Ranking de Vendedores (Sempre traz a lista completa para o filtro)
            cursor.execute(ComercialQueries.get_performance_vendedores(inicio, fim))
            vendedores = cursor.fetchall()

            # 3. Busca Motivos de Cancelamento - Passando vendedor_id
            cursor.execute(ComercialQueries.get_motivos_evasao(inicio, fim, vendedor_id))
            motivos = cursor.fetchall()

            # --- Tratamento de Dados e Regras de Negócio ---

            # Garante valores seguros para cálculos
            base_ativa = resumo['base_ativa'] if resumo and resumo.get('base_ativa') else 0
            qtd_ativacoes = resumo['ativacoes'] if resumo and resumo.get('ativacoes') else 0
            qtd_cancelamentos = resumo['cancelamentos'] if resumo and resumo.get('cancelamentos') else 0

            # Cálculo da Taxa de Churn Real
            churn_percentual = 0
            if base_ativa > 0:
                churn_percentual = round((qtd_cancelamentos / base_ativa) * 100, 2)

            return {
                "ativacoes": qtd_ativacoes,
                "cancelamentos": qtd_cancelamentos,
                "crescimento_liquido": qtd_ativacoes - qtd_cancelamentos,
                "ticket_medio_geral": float(resumo['ticket_medio'] or 0) if resumo else 0,
                "churn_rate": churn_percentual,
                "base_ativa": base_ativa,
                "vendedores": vendedores, # Contém id_vendedor e nome_vendedor
                "motivos": motivos       # Agora com nomes reais dos motivos
            }

        except Exception as e:
            print(f"Erro crítico no ComercialService: {e}")
            return {
                "ativacoes": 0, "cancelamentos": 0, "crescimento_liquido": 0,
                "ticket_medio_geral": 0, "churn_rate": 0, "base_ativa": 0,
                "vendedores": [], "motivos": []
            }
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
