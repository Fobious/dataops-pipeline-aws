# =============================================================================================================================================
# 2.2 - Aplicação
#  script de aplicação automática de LF-Tags nas colunas identificadas como PII, utilizando o relatório gerado pelo detect_pii.py para identificar quais colunas devem receber a tag de classificação "PII". O script utiliza o AWS SDK (boto3) para interagir com o AWS Lake Formation e aplicar as tags nas colunas da tabela especificada.
# ====================================================================================================================================
import json
from pathlib import Path
import boto3
from botocore.exceptions import ClientError


DATABASE_NAME = "dataops_governanca_db"
TABLE_NAME = "clientes"
TAG_KEY = "classificacao"
TAG_VALUE = "PII"
REPORT_PATH = Path("reports/pii_scan_report.json")

#trazendo as colunas identificadas como PII no relatório gerado pelo detect_pii.py, para aplicar as LF-Tags automaticamente nessas colunas.
def carregar_colunas_pii():
    if not REPORT_PATH.exists():
        raise FileNotFoundError(
            f"Relatório não encontrado: {REPORT_PATH}. Execute primeiro pii/detect_pii.py"
        )

    with open(REPORT_PATH, "r", encoding="utf-8") as arquivo:
        relatorio = json.load(arquivo)

    colunas = [
        item["coluna"]
        for item in relatorio.get("colunas_pii_identificadas", [])
        if item.get("classificacao") == "PII"
    ]

    return sorted(set(colunas))


def obter_account_id():
    sts = boto3.client("sts")
    return sts.get_caller_identity()["Account"]


def criar_lf_tag(lakeformation):
    try:
        lakeformation.create_lf_tag(
            TagKey=TAG_KEY,
            TagValues=[TAG_VALUE],
        )
        print(f"LF-Tag criada: {TAG_KEY}={TAG_VALUE}")

    except ClientError as erro:
        codigo = erro.response["Error"]["Code"]

        if codigo == "AlreadyExistsException":
            print(f"LF-Tag já existe: {TAG_KEY}={TAG_VALUE}")
        else:
            raise


def aplicar_tag_nas_colunas(lakeformation, catalog_id, colunas_pii):
    if not colunas_pii:
        print("Nenhuma coluna PII encontrada no relatório.")
        return

    lakeformation.add_lf_tags_to_resource(
        Resource={
            "TableWithColumns": {
                "CatalogId": catalog_id,
                "DatabaseName": DATABASE_NAME,
                "Name": TABLE_NAME,
                "ColumnNames": colunas_pii,
            }
        },
        LFTags=[
            {
                "TagKey": TAG_KEY,
                "TagValues": [TAG_VALUE],
            }
        ],
    )

    print("LF-Tag aplicada com sucesso nas colunas:")
    for coluna in colunas_pii:
        print(f"- {coluna}: {TAG_KEY}={TAG_VALUE}")


def main():
    colunas_pii = carregar_colunas_pii()
    catalog_id = obter_account_id()
    lakeformation = boto3.client("lakeformation", region_name="us-east-1")

    print("========================================")
    print("APLICAÇÃO AUTOMÁTICA DE LF-TAGS")
    print("========================================")
    print(f"Database: {DATABASE_NAME}")
    print(f"Tabela: {TABLE_NAME}")
    print(f"Colunas PII identificadas: {', '.join(colunas_pii)}")

    criar_lf_tag(lakeformation)
    aplicar_tag_nas_colunas(lakeformation, catalog_id, colunas_pii)

    print("========================================")
    print("PROCESSO CONCLUÍDO")
    print("========================================")


if __name__ == "__main__":
    main()