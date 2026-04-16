-- @QUERY_PASSIVO_TOTAL
-- Soma tudo o que está aberto, mas respeitando o período de vencimento selecionado
SELECT COALESCE(ROUND(SUM(valor_aberto), 2), 0) AS total
FROM ixcprovedor.fn_apagar
WHERE status = 'A' 
  AND data_vencimento BETWEEN :inicio AND :fim;

-- @QUERY_PASSIVO_VENCIDO
-- Soma o que está aberto e com vencimento menor que o início do período selecionado (ou menor que hoje)
SELECT COALESCE(ROUND(SUM(valor_aberto), 2), 0) AS total
FROM ixcprovedor.fn_apagar
WHERE status = 'A' 
  AND data_vencimento < :inicio;

-- @QUERY_SUSTENTABILIDADE
-- Calcula a relação de Pagos vs Abertos dentro do período selecionado
SELECT COALESCE(ROUND((SUM(CASE WHEN status = 'R' THEN valor_pago ELSE 0 END) /
       NULLIF(SUM(CASE WHEN status = 'A' THEN valor_aberto ELSE 0 END), 0)) * 100, 2), 0) AS total
FROM ixcprovedor.fn_apagar
WHERE data_vencimento BETWEEN :inicio AND :fim;

-- @QUERY_PRESSAO_30D
-- Projeção de 30 dias a partir do fim do período selecionado
SELECT COALESCE(ROUND(SUM(valor_aberto), 2), 0) AS total
FROM ixcprovedor.fn_apagar
WHERE status = 'A' 
  AND data_vencimento BETWEEN :fim AND DATE_ADD(:fim, INTERVAL 30 DAY);

-- @QUERY_PROJECAO_90D
-- Projeção de 90 dias a partir do fim do período selecionado
SELECT COALESCE(ROUND(SUM(valor_aberto), 2), 0) AS total
FROM ixcprovedor.fn_apagar
WHERE status = 'A' 
  AND data_vencimento BETWEEN :fim AND DATE_ADD(:fim, INTERVAL 90 DAY);

-- @QUERY_CRESCIMENTO_REAL
SELECT 0 AS total;



-- @QUERY_TOP_FORNECEDORES
SELECT 
    f.razao AS fornecedor,
    ROUND(SUM(a.valor_aberto + a.valor_pago), 2) AS total
FROM ixcprovedor.fn_apagar a
JOIN ixcprovedor.fornecedor f ON a.id_fornecedor = f.id
WHERE a.data_vencimento BETWEEN :inicio AND :fim
GROUP BY f.id, f.razao
ORDER BY total DESC
LIMIT 5;




