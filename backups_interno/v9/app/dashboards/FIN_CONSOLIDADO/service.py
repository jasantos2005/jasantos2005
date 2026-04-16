import mysql.connector
from app.config import settings

class ConsolidadoService:
    def __init__(self):
        self.config = {
            'host': settings.DB_HOST, 'user': settings.DB_USER,
            'password': settings.DB_PASS, 'database': settings.DB_NAME, 'port': settings.DB_PORT
        }

    def get_fluxo_caixa(self, inicio, fim):
        conn = None
        try:
            conn = mysql.connector.connect(**self.config)
            cursor = conn.cursor(dictionary=True)

            # 1. Busca de Totais Gerais (Cards)
            sql_totais = f"""
            SELECT 
                (SELECT COALESCE(SUM(valor_aberto), 0) FROM ixcprovedor.fn_areceber WHERE data_vencimento BETWEEN '{inicio}' AND '{fim}' AND status = 'A') as rec_aberto,
                (SELECT COALESCE(SUM(valor_recebido), 0) FROM ixcprovedor.fn_areceber WHERE data_vencimento BETWEEN '{inicio}' AND '{fim}' AND status = 'R') as rec_pago,
                (SELECT COALESCE(SUM(valor_aberto), 0) FROM ixcprovedor.fn_apagar WHERE data_vencimento BETWEEN '{inicio}' AND '{fim}' AND status = 'A') as pag_aberto,
                (SELECT COALESCE(SUM(valor_total_pago), 0) FROM ixcprovedor.fn_apagar WHERE data_vencimento BETWEEN '{inicio}' AND '{fim}' AND status = 'R') as pag_pago
            """
            cursor.execute(sql_totais)
            res_totais = cursor.fetchone()

            # 2. Busca de Evolução Diária (Para o Gráfico de Linhas)
            # Usamos DATE_FORMAT para garantir que o JS leia a data corretamente
            sql_timeline = f"""
            SELECT data_ref, SUM(receita) as receita, SUM(despesa) as despesa FROM (
                SELECT data_vencimento as data_ref, valor_aberto as receita, 0 as despesa 
                FROM ixcprovedor.fn_areceber WHERE data_vencimento BETWEEN '{inicio}' AND '{fim}'
                UNION ALL
                SELECT data_vencimento as data_ref, 0 as receita, valor_aberto as despesa 
                FROM ixcprovedor.fn_apagar WHERE data_vencimento BETWEEN '{inicio}' AND '{fim}'
            ) as timeline 
            GROUP BY data_ref 
            ORDER BY data_ref
            """
            cursor.execute(sql_timeline)
            res_timeline = cursor.fetchall()

            # Processamento de valores
            r_aberto = float(res_totais['rec_aberto'] or 0)
            r_pago = float(res_totais['rec_pago'] or 0)
            p_aberto = float(res_totais['pag_aberto'] or 0)
            p_pago = float(res_totais['pag_pago'] or 0)

            receber_total = r_aberto + r_pago
            pagar_total = p_aberto + p_pago

            # Formata a timeline para o Chart.js (converte datas para string)
            timeline_formatada = []
            for row in res_timeline:
                timeline_formatada.append({
                    "data_ref": str(row['data_ref']),
                    "receita": float(row['receita'] or 0),
                    "despesa": float(row['despesa'] or 0)
                })

            return {
                "receber": receber_total,
                "pagar": pagar_total,
                "saldo_previsto": receber_total - pagar_total,
                "realizado_liquido": r_pago - p_pago,
                "timeline": timeline_formatada,
                "indices": {
                    "comprometimento": round((pagar_total / receber_total * 100), 2) if receber_total > 0 else 0
                }
            }

        except Exception as e:
            print(f"Erro Crítico no Consolidado: {e}")
            return {
                "receber": 0, "pagar": 0, "saldo_previsto": 0, 
                "realizado_liquido": 0, "timeline": [], "indices": {"comprometimento": 0}
            }
        finally:
            if conn and conn.is_connected():
                cursor.close()
                conn.close()
