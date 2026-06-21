# TP3 — Definição da Tabela de Features para Machine Learning

## Objetivo

A camada `features_clientes_ml` foi criada como uma Feature Store lógica para disponibilizar variáveis preditivas limpas para cientistas de dados.

O objetivo é permitir que um cientista de dados acesse dados já tratados e agregados por cliente, sem precisar refazer a limpeza, joins ou cálculos a partir das tabelas brutas de clientes, vendas e produtos.

---

## Localização da camada

- Serviço de consulta: Amazon Athena
- Catálogo: AWS Glue Data Catalog
- Database: `dataops_governanca_db`
- View: `features_clientes_ml`

---

## Fontes utilizadas

A view foi criada a partir das seguintes tabelas catalogadas no Glue Data Catalog:

| Tabela | Finalidade |
|---|---|
| `clientes` | Dados cadastrais dos clientes |
| `vendas` | Histórico de compras realizadas |
| `produtos` | Base de produtos utilizada no consumo analítico |

---

## Definição das features

| Coluna | Tipo lógico | Descrição |
|---|---|---|
| `id_cliente` | Identificador | Chave do cliente usada para relacionar as features ao indivíduo analisado |
| `uf` | Categórica | Unidade federativa do cliente |
| `status_cliente` | Categórica | Status cadastral do cliente |
| `qtd_compras_total` | Numérica | Quantidade total de compras realizadas pelo cliente |
| `valor_total_compras` | Numérica | Valor total comprado pelo cliente em todo o histórico |
| `ticket_medio_cliente` | Numérica | Valor médio das compras realizadas pelo cliente |
| `media_compras_ultimos_6_meses` | Numérica | Média mensal de compras no período recente considerado |
| `score_cliente` | Categórica | Classificação simples do cliente em baixo, médio ou alto valor |

---

## Justificativa das features

As variáveis foram criadas para representar comportamento de compra e valor do cliente. Elas podem ser utilizadas em modelos de Machine Learning para problemas como:

- Segmentação de clientes;
- Propensão de compra;
- Priorização comercial;
- Classificação de clientes por valor;
- Análise de retenção.

---

## Exemplo de consulta via Athena

```sql
SELECT *
FROM dataops_governanca_db.features_clientes_ml
ORDER BY valor_total_compras DESC;