class ComercialQueries:

    @staticmethod
    def get_resumo_geral(inicio, fim, vendedor_id=None):
        """
        KPI: RESUMO EXECUTIVO COM FILTRO OPCIONAL DE VENDEDOR
        """
        # Filtro dinâmico para vendedor
        condicao_vendedor = f" AND id_vendedor = {vendedor_id}" if vendedor_id else ""
        
        return f"""
        SELECT
            (SELECT COUNT(*) FROM ixcprovedor.cliente_contrato
             WHERE data_ativacao BETWEEN '{inicio}' AND '{fim}' {condicao_vendedor}) as ativacoes,

            (SELECT COUNT(*) FROM ixcprovedor.cliente_contrato
             WHERE data_cancelamento BETWEEN '{inicio}' AND '{fim}' {condicao_vendedor}) as cancelamentos,

            (SELECT AVG(valor_unitario) FROM ixcprovedor.cliente_contrato
             WHERE data_ativacao BETWEEN '{inicio}' AND '{fim}' {condicao_vendedor}) as ticket_medio,

            (SELECT COUNT(*) FROM ixcprovedor.cliente_contrato
             WHERE status = 'A') as base_ativa
        """

    @staticmethod
    def get_performance_vendedores(inicio, fim):
        """
        KPI: PERFORMANCE POR VENDEDOR (Utilizado para Ranking e para o Select de Filtro)
        """
        return f"""
        SELECT
            f.id AS id_vendedor,
            f.funcionario AS nome_vendedor,
            COUNT(cc.id) AS qtd_vendas,
            ROUND(SUM(COALESCE(vdc.valor_contrato, 0)), 2) AS receita_total_vendida
        FROM ixcprovedor.cliente_contrato cc
        LEFT JOIN ixcprovedor.funcionarios f ON f.id = cc.id_vendedor
        LEFT JOIN ixcprovedor.vd_contratos vdc ON vdc.id = cc.id_vd_contrato
        WHERE cc.data_ativacao BETWEEN '{inicio}' AND '{fim}'
        GROUP BY f.id, f.funcionario
        ORDER BY receita_total_vendida DESC;
        """

    @staticmethod
    def get_motivos_evasao(inicio, fim, vendedor_id=None):
        """
        KPI: ANÁLISE DE CHURN COM NOMES REAIS DOS MOTIVOS
        """
        condicao_vendedor = f" AND cc.id_vendedor = {vendedor_id}" if vendedor_id else ""

        return f"""
        SELECT
            m.motivo AS motivo,
            COUNT(cc.id) AS total
        FROM ixcprovedor.cliente_contrato cc
        LEFT JOIN ixcprovedor.fn_areceber_mot_cancelamento m ON m.id = cc.motivo_cancelamento
        WHERE cc.data_cancelamento BETWEEN '{inicio}' AND '{fim}'
          {condicao_vendedor}
        GROUP BY m.motivo
        ORDER BY total DESC
        LIMIT 5;
        """
