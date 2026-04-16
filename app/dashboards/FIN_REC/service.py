import mysql.connector
from app.config import settings
from datetime import date
import os


class FinanceiroService:
    def __init__(self):
        self.config = {
            'host':     settings.DB_HOST,
            'user':     settings.DB_USER,
            'password': settings.DB_PASS,
            'database': settings.DB_NAME,
            'port':     settings.DB_PORT
        }
        self.path_sql = "/opt/automacoes/GSG/gestao/diretoria/dashboards/app/dashboards/FIN_REC/queries.sql"

    def _get_conn(self):
        return mysql.connector.connect(**self.config)

    def _execute_raw(self, sql, params=None, multi=False):
        """Executa SQL direto com parâmetros opcionais."""
        try:
            conn = self._get_conn()
            cursor = conn.cursor(dictionary=True)
            cursor.execute(sql, params or ())
            result = cursor.fetchall() if multi else cursor.fetchone()
            while cursor.nextset():
                pass
            cursor.close()
            conn.close()
            return result if result else ([] if multi else {})
        except Exception as e:
            print(f"[FinanceiroService] Erro SQL: {e}")
            return [] if multi else {}

    def _execute(self, query_name, params=None, multi=False):
        """Lê query do arquivo .sql pelo nome e executa com parâmetros."""
        try:
            if not os.path.exists(self.path_sql):
                print(f"[FinanceiroService] Arquivo SQL não encontrado: {self.path_sql}")
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
                print(f"[FinanceiroService] Query {query_name} não encontrada no SQL.")
                return [] if multi else {}

            return self._execute_raw(sql, params, multi)

        except Exception as e:
            print(f"[FinanceiroService] Erro em {query_name}: {e}")
            return [] if multi else {}

    # ──────────────────────────────────────────────────────────────
    # Helpers de data
    # ──────────────────────────────────────────────────────────────
    def _parse_dates(self, inicio, fim):
        """Retorna (inicio_str, fim_str) com fallback para o mês atual."""
        hoje = date.today()
        if not fim or fim.strip() == "":
            fim = hoje.strftime('%Y-%m-%d')
        if not inicio or inicio.strip() == "":
            inicio = hoje.strftime('%Y-%m-01')
        return inicio, fim

    # ──────────────────────────────────────────────────────────────
    # Resumo (KPIs) — filtrado por periodo
    # ──────────────────────────────────────────────────────────────
    def get_resumo(self, inicio, fim):
        inicio, fim = self._parse_dates(inicio, fim)

        sql_03 = """
            SELECT ROUND(
                (SUM(CASE WHEN COALESCE(pagamento_data, baixa_data) <= data_vencimento THEN valor_recebido ELSE 0 END)
                / NULLIF(SUM(valor_recebido),0))*100, 2) as percentual_no_prazo,
                SUM(valor_recebido) as total_pago_no_prazo
            FROM ixcprovedor.fn_areceber
            WHERE status = 'R'
              AND data_vencimento BETWEEN %s AND %s
        """

        sql_05 = """
            SELECT ROUND(SUM(valor_recebido)/NULLIF(COUNT(DISTINCT id_cliente),0),2) as arpu_real,
                COUNT(DISTINCT id_cliente) as clientes_pagantes
            FROM ixcprovedor.fn_areceber
            WHERE status = 'R' AND pagamento_data BETWEEN %s AND %s
        """

        sql_06 = """
            SELECT ROUND(
                (SUM(CASE WHEN valor_aberto > 0 THEN valor_aberto ELSE 0 END)
                / NULLIF(SUM(valor),0))*100, 2) as percentual_inadimplencia,
                SUM(valor_aberto) as total_ainda_em_aberto,
                SUM(valor) as total_que_venceu_no_mes
            FROM ixcprovedor.fn_areceber
            WHERE status <> 'C'
              AND data_vencimento BETWEEN %s AND %s
        """

        sql_07 = """
            SELECT ROUND((SUM(valor_aberto)/NULLIF(SUM(valor),0))*100,2) as percentual_inadimplencia_ano,
                SUM(valor_aberto) as total_em_aberto_no_ano
            FROM ixcprovedor.fn_areceber
            WHERE status <> 'C' AND data_vencimento BETWEEN %s AND %s
        """

        return {
            "recuperacao_mes_ant":   self._execute('SQL_01'),
            "recuperacao_historica": self._execute('SQL_02'),
            "pagamento_prazo":       self._execute_raw(sql_03, (inicio, fim)),
            "media_atraso":          self._execute('SQL_04'),
            "arpu_caixa":            self._execute_raw(sql_05, (inicio, fim)),
            "inadimplencia_mes":     self._execute_raw(sql_06, (inicio, fim)),
            "inadimplencia_ano":     self._execute_raw(sql_07, (inicio, fim)),
            "inadimplencia_fechada": self._execute('SQL_08'),
            "exposicao_mes":         self._execute('SQL_09'),
            "exposicao_ano":         self._execute('SQL_10'),
        }

    # ──────────────────────────────────────────────────────────────
    # Gráficos — todos filtrados por período
    # ──────────────────────────────────────────────────────────────
    def get_bi_evolucao(self, inicio, fim):
        inicio, fim = self._parse_dates(inicio, fim)
        sql = """
            SELECT DATE_FORMAT(data_vencimento, '%m/%Y') as mes,
                SUM(valor_recebido) as recebido,
                SUM(valor_aberto) as inadimplente
            FROM ixcprovedor.fn_areceber
            WHERE status <> 'C'
              AND data_vencimento BETWEEN %s AND %s
            GROUP BY mes
            ORDER BY MIN(data_vencimento) ASC
        """
        dados_raw = self._execute_raw(sql, (inicio, fim), multi=True)
        return {
            "labels":      [row['mes'] for row in dados_raw] if dados_raw else [],
            "recebido":    [float(row['recebido'] or 0) for row in dados_raw] if dados_raw else [],
            "inadimplente":[float(row['inadimplente'] or 0) for row in dados_raw] if dados_raw else []
        }

    def get_aging_data(self, inicio, fim):
        inicio, fim = self._parse_dates(inicio, fim)
        sql = """
            SELECT
                CASE
                    WHEN DATEDIFF(CURDATE(), data_vencimento) BETWEEN 1 AND 30 THEN '01-30 dias'
                    WHEN DATEDIFF(CURDATE(), data_vencimento) BETWEEN 31 AND 60 THEN '31-60 dias'
                    WHEN DATEDIFF(CURDATE(), data_vencimento) BETWEEN 61 AND 90 THEN '61-90 dias'
                    ELSE 'Acima de 90 dias'
                END AS faixa,
                SUM(valor_aberto) AS valor
            FROM ixcprovedor.fn_areceber
            WHERE status <> 'C'
              AND valor_aberto > 0
              AND data_vencimento BETWEEN %s AND %s
            GROUP BY faixa
            ORDER BY MIN(data_vencimento) DESC
        """
        dados_raw = self._execute_raw(sql, (inicio, fim), multi=True)
        return {
            "labels": [row['faixa'] for row in dados_raw] if dados_raw else [],
            "valores": [float(row['valor'] or 0) for row in dados_raw] if dados_raw else []
        }

    def get_top_devedores(self, inicio, fim):
        inicio, fim = self._parse_dates(inicio, fim)
        sql = """
            SELECT c.razao AS cliente,
                ROUND(SUM(f.valor_aberto), 2) AS total_devido,
                COUNT(f.id) AS qtd_titulos
            FROM ixcprovedor.fn_areceber f
            JOIN ixcprovedor.cliente c ON f.id_cliente = c.id
            WHERE f.status <> 'C'
              AND f.valor_aberto > 0
              AND f.data_vencimento BETWEEN %s AND %s
            GROUP BY f.id_cliente
            ORDER BY total_devido DESC
            LIMIT 10
        """
        result = self._execute_raw(sql, (inicio, fim), multi=True)
        return result if result else []

    def get_fluxo_caixa(self, inicio, fim):
        inicio, fim = self._parse_dates(inicio, fim)
        sql = """
            SELECT
                SUM(CASE WHEN tipo = 'ENTRADA' THEN valor ELSE 0 END) AS total_entradas,
                SUM(CASE WHEN tipo = 'SAIDA' THEN valor ELSE 0 END) AS total_saidas,
                SUM(CASE WHEN tipo = 'ENTRADA' THEN valor WHEN tipo = 'SAIDA' THEN -valor ELSE 0 END) AS resultado_mes
            FROM (
                SELECT 'ENTRADA' AS tipo, ar.valor_recebido AS valor
                FROM ixcprovedor.fn_areceber ar
                WHERE ar.status = 'R'
                  AND ar.baixa_data BETWEEN %s AND %s
                UNION ALL
                SELECT 'SAIDA' AS tipo, ap.valor_total_pago AS valor
                FROM ixcprovedor.fn_apagar ap
                WHERE ap.data_pagamento BETWEEN %s AND %s
                  AND ap.valor_total_pago > 0
            ) fluxo
        """
        result = self._execute_raw(sql, (inicio, fim, inicio, fim))
        if result:
            return {
                "entradas":  float(result.get('total_entradas') or 0),
                "saidas":    float(result.get('total_saidas') or 0),
                "resultado": float(result.get('resultado_mes') or 0)
            }
        return {"entradas": 0, "saidas": 0, "resultado": 0}

    def get_sparklines(self):
        """Retorna tendência dos últimos 6 meses para os mini-gráficos dos KPI cards."""
        sql_prazo = """
            SELECT DATE_FORMAT(data_vencimento, '%b/%y') as mes,
                ROUND((SUM(CASE WHEN COALESCE(pagamento_data, baixa_data) <= data_vencimento
                    THEN valor_recebido ELSE 0 END) / NULLIF(SUM(valor_recebido),0))*100, 1) as val
            FROM ixcprovedor.fn_areceber
            WHERE status = 'R'
              AND data_vencimento >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY DATE_FORMAT(data_vencimento, '%Y-%m')
            ORDER BY MIN(data_vencimento)
        """
        sql_inad = """
            SELECT DATE_FORMAT(data_vencimento, '%b/%y') as mes,
                ROUND((SUM(CASE WHEN valor_aberto > 0 THEN valor_aberto ELSE 0 END)
                / NULLIF(SUM(valor),0))*100, 1) as val
            FROM ixcprovedor.fn_areceber
            WHERE status <> 'C'
              AND data_vencimento >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY DATE_FORMAT(data_vencimento, '%Y-%m')
            ORDER BY MIN(data_vencimento)
        """
        sql_arpu = """
            SELECT DATE_FORMAT(pagamento_data, '%b/%y') as mes,
                ROUND(SUM(valor_recebido)/NULLIF(COUNT(DISTINCT id_cliente),0), 2) as val
            FROM ixcprovedor.fn_areceber
            WHERE status = 'R'
              AND pagamento_data >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY DATE_FORMAT(pagamento_data, '%Y-%m')
            ORDER BY MIN(pagamento_data)
        """
        prazo = self._execute_raw(sql_prazo, multi=True) or []
        inad  = self._execute_raw(sql_inad,  multi=True) or []
        arpu  = self._execute_raw(sql_arpu,  multi=True) or []
        return {
            "labels": [r['mes'] for r in prazo],
            "prazo":  [float(r['val'] or 0) for r in prazo],
            "inad":   [float(r['val'] or 0) for r in inad],
            "arpu":   [float(r['val'] or 0) for r in arpu],
        }

    def get_performance_mensal(self, inicio, fim):
        inicio, fim = self._parse_dates(inicio, fim)
        sql = """
            SELECT
                DATE_FORMAT(data_vencimento, '%Y-%m') AS mes_ref,
                COUNT(id) AS total_titulos,
                ROUND(SUM(valor), 2) AS valor_faturado,
                ROUND(SUM(CASE WHEN valor_aberto > 0 AND data_vencimento < CURDATE() THEN valor_aberto ELSE 0 END), 2) AS saldo_vencido,
                ROUND(SUM(CASE WHEN status = 'R' THEN valor_recebido ELSE 0 END), 2) AS total_recebido,
                ROUND(
                    COALESCE(
                        (SUM(CASE WHEN valor_aberto > 0 AND data_vencimento < CURDATE() THEN valor_aberto ELSE 0 END) /
                        NULLIF(SUM(valor), 0)) * 100,
                    0), 2
                ) AS percentual_inadimplencia
            FROM ixcprovedor.fn_areceber
            WHERE data_vencimento BETWEEN %s AND %s
              AND status <> 'C'
            GROUP BY 1
            ORDER BY 1 ASC
        """
        dados_raw = self._execute_raw(sql, (inicio, fim), multi=True)
        if not dados_raw:
            return {"labels": [], "faturado": [], "recebido": [], "vencido": [], "perc_inad": []}
        return {
            "labels":    [row['mes_ref'] for row in dados_raw],
            "faturado":  [float(row['valor_faturado'] or 0) for row in dados_raw],
            "recebido":  [float(row['total_recebido'] or 0) for row in dados_raw],
            "vencido":   [float(row['saldo_vencido'] or 0) for row in dados_raw],
            "perc_inad": [float(row['percentual_inadimplencia'] or 0) for row in dados_raw],
        }
