CREATE OR REPLACE VIEW dataops_governanca_db.features_clientes_ml AS
SELECT
    c.id_cliente,
    c.uf,
    c.status_cliente,

    COUNT(v.id_venda) AS qtd_compras_total,

    ROUND(SUM(v.quantidade * v.valor_unitario), 2) AS valor_total_compras,

    ROUND(AVG(v.quantidade * v.valor_unitario), 2) AS ticket_medio_cliente,

    ROUND(
        SUM(
            CASE
                WHEN date_parse(v.data_venda, '%Y-%m-%d') >= DATE '2026-05-01'
                THEN v.quantidade * v.valor_unitario
                ELSE 0
            END
        ) / 6,
        2
    ) AS media_compras_ultimos_6_meses,

    CASE
        WHEN SUM(v.quantidade * v.valor_unitario) >= 7000 THEN 'alto_valor'
        WHEN SUM(v.quantidade * v.valor_unitario) >= 3000 THEN 'medio_valor'
        ELSE 'baixo_valor'
    END AS score_cliente

FROM dataops_governanca_db.clientes c
LEFT JOIN dataops_governanca_db.vendas v
    ON c.id_cliente = v.id_cliente

GROUP BY
    c.id_cliente,
    c.uf,
    c.status_cliente;