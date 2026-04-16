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
