class TecnicoQueries:
    @staticmethod
    def get_resumo_kpis(inicio, fim):
        """
        Consolida os KPIs 01, 02, 03, 05, 06 e 07.
        Foca no volume, eficiência (SLA) e qualidade (Reincidência).
        """
        return f"""
        SELECT 
            -- KPI 01: Volume Total de OS abertas no período
            COUNT(*) AS total_os,
            
            -- KPI 02: OS Finalizadas (Eficiência)
            COUNT(CASE WHEN status = 'F' THEN 1 END) AS os_finalizadas,
            
            -- KPI 03: % SLA Cumprido
            ROUND(
                (SUM(CASE WHEN status_sla = 'S' THEN 1 ELSE 0 END) / COUNT(*)) * 100, 2
            ) AS sla_percentual,
            
            -- KPI 05: Taxa de Reincidência (Assunto 287 dividido pelo total de suporte 285/287)
            ROUND(
                (SUM(CASE WHEN id_assunto = 287 THEN 1 ELSE 0 END) / 
                 NULLIF(SUM(CASE WHEN id_assunto IN (285, 287) THEN 1 ELSE 0 END), 0)
                ) * 100, 2
            ) AS taxa_reincidencia,
            
            -- KPI 06: Instalações Realizadas (FTTH - Assunto 311)
            SUM(CASE WHEN id_assunto = 311 AND status = 'F' THEN 1 ELSE 0 END) AS instalacoes_feitas,
            
            -- KPI 07: Manutenções de Rede (Assuntos 431 e 433)
            SUM(CASE WHEN id_assunto IN (431, 433) THEN 1 ELSE 0 END) AS manutencoes_rede
            
        FROM ixcprovedor.su_oss_chamado
        WHERE data_abertura BETWEEN '{inicio}' AND '{fim}'
        AND id_assunto IN (311, 439, 344, 285, 287, 441, 433, 431)
        """

    @staticmethod
    def get_produtividade_tecnicos(inicio, fim):
        """
        KPI 08: Ranking de produtividade separando SERVIÇO (19) de SUPORTE (20).
        """
        return f"""
        SELECT 
            f.funcionario AS tecnico,
            COUNT(CASE WHEN c.setor = 19 THEN 1 END) AS total_servicos,
            COUNT(CASE WHEN c.setor = 20 THEN 1 END) AS total_suportes,
            COUNT(*) AS total_geral
        FROM ixcprovedor.su_oss_chamado c
        LEFT JOIN ixcprovedor.funcionarios f ON f.id = c.id_tecnico
        WHERE c.status = 'F'
        AND c.data_final BETWEEN '{inicio}' AND '{fim}'
        AND c.setor IN (19, 20)
        GROUP BY c.id_tecnico
        ORDER BY total_geral DESC
        """

    @staticmethod
    def get_distribuicao_setor(inicio, fim):
        """
        Gera os dados para o gráfico de pizza (Setor 19 vs 20).
        """
        return f"""
        SELECT 
            CASE WHEN setor = 19 THEN 'SERVIÇO' ELSE 'SUPORTE' END AS setor_nome,
            COUNT(*) AS total
        FROM ixcprovedor.su_oss_chamado
        WHERE status = 'F'
        AND data_final BETWEEN '{inicio}' AND '{fim}'
        AND setor IN (19, 20)
        GROUP BY setor
        """
