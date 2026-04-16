import mysql.connector
from app.config import settings
from datetime import date, timedelta


class ComercialService:
    def __init__(self):
        self.config = {
            'host':     settings.DB_HOST,
            'user':     settings.DB_USER,
            'password': settings.DB_PASS,
            'database': settings.DB_NAME,
            'port':     settings.DB_PORT
        }

    def _get_conn(self):
        return mysql.connector.connect(**self.config)

    def _exec(self, sql, params=None, multi=False):
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
            print(f"[ComercialService] Erro SQL: {e}")
            return [] if multi else {}

    def _parse_dates(self, inicio, fim):
        hoje = date.today()
        if not fim or fim.strip() == "":
            fim = hoje.strftime('%Y-%m-%d')
        if not inicio or inicio.strip() == "":
            inicio = hoje.strftime('%Y-%m-01')
        return inicio, fim

    def _dates_for_periodo(self, periodo):
        hoje = date.today()
        fim = hoje.strftime('%Y-%m-%d')
        if periodo == 'trimestre':
            inicio = (hoje - timedelta(days=90)).strftime('%Y-%m-%d')
        elif periodo == 'semestre':
            inicio = (hoje - timedelta(days=180)).strftime('%Y-%m-%d')
        elif periodo == 'ano':
            inicio = hoje.strftime('%Y-01-01')
        else:  # mes
            inicio = hoje.strftime('%Y-%m-01')
        return inicio, fim

    # ──────────────────────────────────────────────────────────────
    # KPI Cards — filtrado por periodo/datas
    # ──────────────────────────────────────────────────────────────
    def get_resumo(self, inicio, fim):
        inicio, fim = self._parse_dates(inicio, fim)

        sql_kpi = """
            SELECT
                (SELECT COUNT(*) FROM ixcprovedor.cliente_contrato
                 WHERE data_ativacao BETWEEN %s AND %s) AS ativacoes,
                (SELECT COUNT(*) FROM ixcprovedor.cliente_contrato
                 WHERE data_cancelamento BETWEEN %s AND %s) AS cancelamentos,
                (SELECT ROUND(AVG(vdc.valor_contrato), 2)
                 FROM ixcprovedor.cliente_contrato cc
                 JOIN ixcprovedor.vd_contratos vdc ON vdc.id = cc.id_vd_contrato
                 WHERE cc.data_ativacao BETWEEN %s AND %s) AS ticket_medio,
                (SELECT COUNT(*) FROM ixcprovedor.cliente_contrato
                 WHERE status = 'A') AS base_ativa
        """
        r = self._exec(sql_kpi, (inicio, fim, inicio, fim, inicio, fim))

        ativacoes      = int(r.get('ativacoes') or 0) if r else 0
        cancelamentos  = int(r.get('cancelamentos') or 0) if r else 0
        base_ativa     = int(r.get('base_ativa') or 0) if r else 0
        ticket_medio   = float(r.get('ticket_medio') or 0) if r else 0
        churn_rate     = round((cancelamentos / base_ativa) * 100, 2) if base_ativa > 0 else 0

        return {
            "ativacoes":           ativacoes,
            "cancelamentos":       cancelamentos,
            "crescimento_liquido": ativacoes - cancelamentos,
            "ticket_medio":        ticket_medio,
            "churn_rate":          churn_rate,
            "base_ativa":          base_ativa,
        }

    # ──────────────────────────────────────────────────────────────
    # Ranking de Vendedores — por período predefinido
    # ──────────────────────────────────────────────────────────────
    def get_ranking(self, periodo='mes'):
        inicio, fim = self._dates_for_periodo(periodo)

        sql = """
            SELECT
                f.id AS id_vendedor,
                COALESCE(f.funcionario, 'Sem Vendedor') AS nome,
                COUNT(cc.id) AS ativacoes,
                ROUND(COALESCE(SUM(vdc.valor_contrato), 0), 2) AS receita,
                ROUND(COALESCE(AVG(vdc.valor_contrato), 0), 2) AS ticket_medio,
                (SELECT COUNT(*) FROM ixcprovedor.cliente_contrato cc2
                 WHERE cc2.id_vendedor = f.id
                   AND cc2.data_cancelamento BETWEEN %s AND %s) AS cancelamentos
            FROM ixcprovedor.cliente_contrato cc
            LEFT JOIN ixcprovedor.funcionarios f ON f.id = cc.id_vendedor
            LEFT JOIN ixcprovedor.vd_contratos vdc ON vdc.id = cc.id_vd_contrato
            WHERE cc.data_ativacao BETWEEN %s AND %s
              AND f.id IS NOT NULL
            GROUP BY f.id, f.funcionario
            ORDER BY ativacoes DESC
        """
        rows = self._exec(sql, (inicio, fim, inicio, fim), multi=True)
        if not rows:
            return []

        max_atv = max((int(r.get('ativacoes') or 0) for r in rows), default=1)

        result = []
        for i, r in enumerate(rows):
            atv  = int(r.get('ativacoes') or 0)
            canc = int(r.get('cancelamentos') or 0)
            score = round((atv / max_atv) * 100, 0) if max_atv > 0 else 0
            result.append({
                "posicao":     i + 1,
                "id":          r['id_vendedor'],
                "nome":        r['nome'],
                "ativacoes":   atv,
                "cancelamentos": canc,
                "crescimento": atv - canc,
                "receita":     float(r.get('receita') or 0),
                "ticket_medio":float(r.get('ticket_medio') or 0),
                "score":       int(score),
            })
        return result

    # ──────────────────────────────────────────────────────────────
    # Evolução Mensal — últimos N meses
    # ──────────────────────────────────────────────────────────────
    def get_evolucao(self, periodo='mes'):
        if periodo in ('trimestre',):
            meses = 3
        elif periodo == 'semestre':
            meses = 6
        elif periodo == 'ano':
            meses = 12
        else:
            meses = 6  # default: sempre mostra 6 meses de contexto

        sql = """
            SELECT
                DATE_FORMAT(data_ativacao, '%m/%Y') AS mes,
                COUNT(id) AS ativacoes,
                SUM(CASE WHEN data_cancelamento IS NOT NULL THEN 1 ELSE 0 END) AS cancelamentos
            FROM ixcprovedor.cliente_contrato
            WHERE data_ativacao >= DATE_SUB(CURDATE(), INTERVAL %s MONTH)
            GROUP BY DATE_FORMAT(data_ativacao, '%%Y-%%m'), DATE_FORMAT(data_ativacao, '%%m/%%Y')
            ORDER BY MIN(data_ativacao) ASC
        """
        rows = self._exec(sql, (meses,), multi=True)
        return {
            "labels":        [r['mes'] for r in rows] if rows else [],
            "ativacoes":     [int(r['ativacoes'] or 0) for r in rows] if rows else [],
            "cancelamentos": [int(r['cancelamentos'] or 0) for r in rows] if rows else [],
        }

    # ──────────────────────────────────────────────────────────────
    # Motivos de Cancelamento
    # ──────────────────────────────────────────────────────────────
    def get_motivos(self, periodo='mes'):
        inicio, fim = self._dates_for_periodo(periodo)
        sql = """
            SELECT
                COALESCE(m.motivo, 'Não informado') AS motivo,
                COUNT(cc.id) AS total
            FROM ixcprovedor.cliente_contrato cc
            LEFT JOIN ixcprovedor.fn_areceber_mot_cancelamento m ON m.id = cc.motivo_cancelamento
            WHERE cc.data_cancelamento BETWEEN %s AND %s
            GROUP BY m.motivo
            ORDER BY total DESC
            LIMIT 6
        """
        rows = self._exec(sql, (inicio, fim), multi=True)
        return {
            "labels": [r['motivo'] for r in rows] if rows else [],
            "valores": [int(r['total'] or 0) for r in rows] if rows else [],
        }

    # ──────────────────────────────────────────────────────────────
    # Produtividade mensal por vendedor (últimos 6 meses)
    # ──────────────────────────────────────────────────────────────
    def get_produtividade(self):
        sql = """
            SELECT
                f.funcionario AS nome,
                DATE_FORMAT(cc.data_ativacao, '%m/%Y') AS mes,
                COUNT(cc.id) AS ativacoes,
                ROUND(COALESCE(SUM(vdc.valor_contrato), 0), 2) AS receita
            FROM ixcprovedor.cliente_contrato cc
            JOIN ixcprovedor.funcionarios f ON f.id = cc.id_vendedor
            LEFT JOIN ixcprovedor.vd_contratos vdc ON vdc.id = cc.id_vd_contrato
            WHERE cc.data_ativacao >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
              AND f.id IS NOT NULL
            GROUP BY f.funcionario, DATE_FORMAT(cc.data_ativacao, '%%Y-%%m'), DATE_FORMAT(cc.data_ativacao, '%%m/%%Y')
            ORDER BY f.funcionario, MIN(cc.data_ativacao)
        """
        rows = self._exec(sql, multi=True)
        if not rows:
            return {"vendedores": [], "meses": [], "dados": {}}

        meses = []
        seen_meses = set()
        for r in rows:
            if r['mes'] not in seen_meses:
                meses.append(r['mes'])
                seen_meses.add(r['mes'])

        dados = {}
        for r in rows:
            nome = r['nome']
            if nome not in dados:
                dados[nome] = {m: 0 for m in meses}
            dados[nome][r['mes']] = int(r['ativacoes'] or 0)

        return {
            "vendedores": list(dados.keys()),
            "meses": meses,
            "dados": dados,
        }

    # ──────────────────────────────────────────────────────────────
    # Vendas por Bairro
    # ──────────────────────────────────────────────────────────────
    def get_vendas_por_bairro(self, periodo='mes'):
        inicio, fim = self._dates_for_periodo(periodo)
        sql = """
            SELECT TRIM(c.bairro) AS bairro, COUNT(cc.id) AS ativacoes
            FROM ixcprovedor.cliente_contrato cc
            JOIN ixcprovedor.cliente c ON c.id = cc.id_cliente
            WHERE cc.data_ativacao BETWEEN %s AND %s
              AND c.bairro IS NOT NULL AND TRIM(c.bairro) != ''
            GROUP BY TRIM(c.bairro)
            ORDER BY ativacoes DESC
            LIMIT 12
        """
        rows = self._exec(sql, (inicio, fim), multi=True)
        return {
            "labels":  [r['bairro'] for r in rows] if rows else [],
            "valores": [int(r['ativacoes'] or 0) for r in rows] if rows else [],
        }

    # ──────────────────────────────────────────────────────────────
    # Perfil individual de vendedor
    # ──────────────────────────────────────────────────────────────
    def get_perfil_vendedor(self, vendedor_id, periodo='mes'):
        inicio, fim = self._dates_for_periodo(periodo)

        # KPIs do período
        sql_kpi = """
            SELECT
                f.funcionario AS nome,
                COUNT(cc.id) AS ativacoes,
                ROUND(COALESCE(SUM(vdc.valor_contrato), 0), 2) AS receita,
                ROUND(COALESCE(AVG(vdc.valor_contrato), 0), 2) AS ticket_medio,
                (SELECT COUNT(*) FROM ixcprovedor.cliente_contrato cc2
                 WHERE cc2.id_vendedor = %s
                   AND cc2.data_cancelamento BETWEEN %s AND %s) AS cancelamentos
            FROM ixcprovedor.cliente_contrato cc
            JOIN ixcprovedor.funcionarios f ON f.id = cc.id_vendedor
            LEFT JOIN ixcprovedor.vd_contratos vdc ON vdc.id = cc.id_vd_contrato
            WHERE cc.id_vendedor = %s
              AND cc.data_ativacao BETWEEN %s AND %s
        """
        kpi = self._exec(sql_kpi, (vendedor_id, inicio, fim, vendedor_id, inicio, fim))

        # Evolução 6 meses
        sql_evolucao = """
            SELECT DATE_FORMAT(cc.data_ativacao, '%m/%Y') AS mes,
                   COUNT(cc.id) AS ativacoes,
                   ROUND(COALESCE(SUM(vdc.valor_contrato), 0), 2) AS receita
            FROM ixcprovedor.cliente_contrato cc
            LEFT JOIN ixcprovedor.vd_contratos vdc ON vdc.id = cc.id_vd_contrato
            WHERE cc.id_vendedor = %s
              AND cc.data_ativacao >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
            GROUP BY DATE_FORMAT(cc.data_ativacao, '%%Y-%%m'), DATE_FORMAT(cc.data_ativacao, '%%m/%%Y')
            ORDER BY MIN(cc.data_ativacao)
        """
        evolucao_rows = self._exec(sql_evolucao, (vendedor_id,), multi=True)

        # Top bairros do vendedor
        sql_bairros = """
            SELECT TRIM(c.bairro) AS bairro, COUNT(cc.id) AS ativacoes
            FROM ixcprovedor.cliente_contrato cc
            JOIN ixcprovedor.cliente c ON c.id = cc.id_cliente
            WHERE cc.id_vendedor = %s
              AND cc.data_ativacao BETWEEN %s AND %s
              AND c.bairro IS NOT NULL AND TRIM(c.bairro) != ''
            GROUP BY TRIM(c.bairro)
            ORDER BY ativacoes DESC
            LIMIT 6
        """
        bairros_rows = self._exec(sql_bairros, (vendedor_id, inicio, fim), multi=True)

        # Últimas ativações
        sql_recentes = """
            SELECT cl.razao AS cliente,
                   TRIM(cl.bairro) AS bairro,
                   cc.data_ativacao,
                   cc.valor_unitario AS valor,
                   cc.status
            FROM ixcprovedor.cliente_contrato cc
            JOIN ixcprovedor.cliente cl ON cl.id = cc.id_cliente
            WHERE cc.id_vendedor = %s
              AND cc.data_ativacao BETWEEN %s AND %s
            ORDER BY cc.data_ativacao DESC
            LIMIT 10
        """
        recentes_rows = self._exec(sql_recentes, (vendedor_id, inicio, fim), multi=True)

        nome = kpi.get('nome', 'Vendedor') if kpi else 'Vendedor'
        atv  = int(kpi.get('ativacoes') or 0) if kpi else 0
        canc = int(kpi.get('cancelamentos') or 0) if kpi else 0

        return {
            "nome":          nome,
            "ativacoes":     atv,
            "cancelamentos": canc,
            "crescimento":   atv - canc,
            "receita":       float(kpi.get('receita') or 0) if kpi else 0,
            "ticket_medio":  float(kpi.get('ticket_medio') or 0) if kpi else 0,
            "evolucao": {
                "labels":   [r['mes'] for r in evolucao_rows] if evolucao_rows else [],
                "ativacoes":[int(r['ativacoes'] or 0) for r in evolucao_rows] if evolucao_rows else [],
                "receita":  [float(r['receita'] or 0) for r in evolucao_rows] if evolucao_rows else [],
            },
            "bairros": {
                "labels":  [r['bairro'] for r in bairros_rows] if bairros_rows else [],
                "valores": [int(r['ativacoes'] or 0) for r in bairros_rows] if bairros_rows else [],
            },
            "recentes": [
                {
                    "cliente":       r['cliente'],
                    "bairro":        r['bairro'] or '—',
                    "data_ativacao": str(r['data_ativacao']),
                    "valor":         float(r['valor'] or 0),
                    "status":        r['status'],
                }
                for r in recentes_rows
            ] if recentes_rows else [],
        }

    # ──────────────────────────────────────────────────────────────
    # Legado — mantido para compatibilidade
    # ──────────────────────────────────────────────────────────────
    def get_dashboard_comercial(self, inicio, fim, vendedor_id=None):
        resumo = self.get_resumo(inicio, fim)
        ranking = self.get_ranking('mes')
        motivos_data = self.get_motivos('mes')
        return {
            **resumo,
            "vendedores": ranking,
            "motivos": [{"motivo": l, "total": v}
                        for l, v in zip(motivos_data["labels"], motivos_data["valores"])],
        }
