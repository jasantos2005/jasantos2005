-- @SQL_01
SELECT ROUND((SUM(valor_recebido)/NULLIF(SUM(valor),0))*100,2) as taxa_recuperacao, SUM(valor_recebido) as total_recuperado FROM ixcprovedor.fn_areceber WHERE status = 'R' AND pagamento_data > data_vencimento AND MONTH(pagamento_data) = MONTH(CURDATE())-1;

-- @SQL_02
SELECT ROUND((SUM(valor_recebido)/NULLIF(SUM(valor),0))*100,2) as taxa_recuperacao_historica FROM ixcprovedor.fn_areceber WHERE status = 'R' AND pagamento_data > data_vencimento;

-- @SQL_03
SELECT ROUND((SUM(CASE WHEN COALESCE(pagamento_data, baixa_data) <= data_vencimento THEN valor_recebido ELSE 0 END)/NULLIF(SUM(valor_recebido),0))*100,2) as percentual_no_prazo, SUM(valor_recebido) as total_pago_no_prazo FROM ixcprovedor.fn_areceber WHERE status = 'R' AND MONTH(data_vencimento) = MONTH(CURDATE());

-- @SQL_04
SELECT ROUND(AVG(DATEDIFF(pagamento_data, data_vencimento)),0) as media_dias_atraso FROM ixcprovedor.fn_areceber WHERE status = 'R' AND pagamento_data > data_vencimento;

-- @SQL_05
SELECT ROUND(SUM(valor_recebido)/NULLIF(COUNT(DISTINCT id_cliente),0),2) as arpu_real, COUNT(DISTINCT id_cliente) as clientes_pagantes FROM ixcprovedor.fn_areceber WHERE status = 'R' AND MONTH(pagamento_data) = MONTH(CURDATE());

-- @SQL_06
SELECT ROUND((SUM(CASE WHEN valor_aberto > 0 THEN valor_aberto ELSE 0 END)/NULLIF(SUM(valor),0))*100,2) as percentual_inadimplencia, SUM(valor_aberto) as total_ainda_em_aberto, SUM(valor) as total_que_venceu_no_mes FROM ixcprovedor.fn_areceber WHERE status <> 'C' AND MONTH(data_vencimento) = MONTH(CURDATE());

-- @SQL_07
SELECT ROUND((SUM(valor_aberto)/NULLIF(SUM(valor),0))*100,2) as percentual_inadimplencia_ano, SUM(valor_aberto) as total_em_aberto_no_ano FROM ixcprovedor.fn_areceber WHERE status <> 'C' AND YEAR(data_vencimento) = YEAR(CURDATE());

-- @SQL_08
SELECT 0 as percentual_inadimplencia_fechado, SUM(valor_aberto) as total_em_aberto_periodo FROM ixcprovedor.fn_areceber WHERE status <> 'C' AND data_vencimento < DATE_SUB(CURDATE(), INTERVAL 90 DAY);

-- @SQL_09
SELECT SUM(valor_aberto) as total_exposto, COUNT(id) as qtd_titulos_vencidos FROM ixcprovedor.fn_areceber WHERE status <> 'C' AND valor_aberto > 0 AND data_vencimento < CURDATE() AND MONTH(data_vencimento) = MONTH(CURDATE());

-- @SQL_10
SELECT SUM(valor_aberto) as total_exposto_ano, COUNT(id) as qtd_titulos_vencidos_ano FROM ixcprovedor.fn_areceber WHERE status <> 'C' AND valor_aberto > 0 AND data_vencimento < CURDATE() AND YEAR(data_vencimento) = YEAR(CURDATE());

-- @SQL_11
SELECT 
    DATE_FORMAT(data_vencimento, '%m/%Y') as mes,
    SUM(valor_recebido) as recebido,
    SUM(valor_aberto) as inadimplente
FROM ixcprovedor.fn_areceber 
WHERE status <> 'C' 
  AND data_vencimento >= DATE_SUB(CURDATE(), INTERVAL 6 MONTH)
GROUP BY mes 
ORDER BY data_vencimento ASC;


-- @SQL_12
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
  AND data_vencimento < CURDATE()
GROUP BY faixa
ORDER BY MIN(data_vencimento) DESC;


-- @SQL_13
SELECT 
    c.razao AS cliente,
    ROUND(SUM(f.valor_aberto), 2) AS total_devido,
    COUNT(f.id) AS qtd_titulos
FROM ixcprovedor.fn_areceber f
JOIN ixcprovedor.cliente c ON f.id_cliente = c.id
WHERE f.status <> 'C' 
  AND f.valor_aberto > 0 
  AND f.data_vencimento < CURDATE()
GROUP BY f.id_cliente
ORDER BY total_devido DESC
LIMIT 10;



-- @SQL_14
SELECT 
    DATE_FORMAT(CURDATE(), '%Y-%m') AS mes_referencia,
    SUM(CASE WHEN tipo = 'ENTRADA' THEN valor ELSE 0 END) AS total_entradas,
    SUM(CASE WHEN tipo = 'SAIDA' THEN valor ELSE 0 END) AS total_saidas,
    SUM(CASE WHEN tipo = 'ENTRADA' THEN valor WHEN tipo = 'SAIDA' THEN -valor ELSE 0 END) AS resultado_mes
FROM (
    SELECT 'ENTRADA' AS tipo, ar.valor_recebido AS valor
    FROM ixcprovedor.fn_areceber ar
    WHERE ar.status = 'R' 
      AND ar.baixa_data >= DATE_FORMAT(CURDATE() ,'%Y-%m-01')
      AND ar.baixa_data <= LAST_DAY(CURDATE())
    UNION ALL
    SELECT 'SAIDA' AS tipo, ap.valor_total_pago AS valor
    FROM ixcprovedor.fn_apagar ap
    WHERE ap.data_pagamento >= DATE_FORMAT(CURDATE() ,'%Y-%m-01')
      AND ap.data_pagamento <= LAST_DAY(CURDATE())
      AND ap.valor_total_pago > 0
) fluxo;




-- @SQL_15
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
WHERE 
    data_vencimento >= DATE_FORMAT(CURDATE(), '%Y-01-01') 
    AND status <> 'C'
GROUP BY 1
ORDER BY 1 ASC;

