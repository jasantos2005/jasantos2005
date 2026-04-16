-- @QUERY_PASSIVO_TOTAL
-- Busca o valor total de títulos em aberto
SELECT ROUND(SUM(valor_aberto), 2) AS total 
FROM ixcprovedor.fn_apagar 
WHERE status = 'A';

-- @QUERY_PASSIVO_VENCIDO
-- Busca o valor total de títulos que já passaram do vencimento
SELECT ROUND(SUM(valor_aberto), 2) AS total 
FROM ixcprovedor.fn_apagar 
WHERE status = 'A' AND data_vencimento < CURDATE();

-- @QUERY_SUSTENTABILIDADE
-- Calcula o Índice de Cobertura (ICR) para o mês atual
SELECT ROUND((SUM(CASE WHEN status = 'R' THEN valor_pago ELSE 0 END) / 
       NULLIF(SUM(CASE WHEN status = 'A' THEN valor_aberto ELSE 0 END), 0)) * 100, 2) AS total 
FROM ixcprovedor.fn_apagar 
WHERE MONTH(data_vencimento) = MONTH(CURDATE());

-- @QUERY_PRESSAO_30D
-- Projeção de pagamentos para os próximos 30 dias
SELECT ROUND(SUM(valor_aberto), 2) AS total 
FROM ixcprovedor.fn_apagar 
WHERE status = 'A' AND data_vencimento BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 30 DAY);

-- @QUERY_PROJECAO_90D
-- Projeção de pagamentos para os próximos 90 dias
SELECT ROUND(SUM(valor_aberto), 2) AS total 
FROM ixcprovedor.fn_apagar 
WHERE status = 'A' AND data_vencimento BETWEEN CURDATE() AND DATE_ADD(CURDATE(), INTERVAL 90 DAY);

-- @QUERY_CRESCIMENTO_REAL
-- Exemplo de cálculo de crescimento (pode ser ajustado conforme sua regra)
SELECT 0 AS total;
