import csv
import json
import re
from datetime import datetime
from pathlib import Path


ARQUIVO_ENTRADA = Path("data/clientes.csv")
PASTA_RELATORIOS = Path("reports")
RELATORIO_JSON = PASTA_RELATORIOS / "pii_scan_report.json"
RELATORIO_TXT = PASTA_RELATORIOS / "pii_scan_report.txt"

LIMITE_DETECCAO = 0.60

PADROES_PII = {
    "CPF": re.compile(r"^\d{3}\.\d{3}\.\d{3}-\d{2}$"),
    "EMAIL": re.compile(r"^[\w\.-]+@[\w\.-]+\.\w+$"),
    "TELEFONE": re.compile(r"^\d{10,11}$"),
}


def carregar_csv(caminho: Path):
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")

    with open(caminho, mode="r", encoding="utf-8") as arquivo:
        leitor = csv.DictReader(arquivo)
        return list(leitor), leitor.fieldnames


def calcular_pii_por_coluna(linhas, colunas):
    resultado = []

    for coluna in colunas:
        valores = [
            str(linha.get(coluna, "")).strip()
            for linha in linhas
            if str(linha.get(coluna, "")).strip()
        ]

        total_valores = len(valores)

        for tipo_pii, regex in PADROES_PII.items():
            total_matches = sum(1 for valor in valores if regex.match(valor))
            taxa_match = total_matches / total_valores if total_valores > 0 else 0

            if taxa_match >= LIMITE_DETECCAO:
                resultado.append({
                    "coluna": coluna,
                    "tipo_pii": tipo_pii,
                    "total_valores_analisados": total_valores,
                    "total_matches": total_matches,
                    "taxa_match": round(taxa_match, 4),
                    "classificacao": "PII",
                    "criterio": f"Regex com taxa >= {LIMITE_DETECCAO:.0%}",
                })

    return resultado


def salvar_relatorios(resultado):
    PASTA_RELATORIOS.mkdir(exist_ok=True)

    relatorio = {
        "data_execucao": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "arquivo_analisado": str(ARQUIVO_ENTRADA),
        "limite_deteccao": LIMITE_DETECCAO,
        "colunas_pii_identificadas": resultado,
    }

    with open(RELATORIO_JSON, mode="w", encoding="utf-8") as arquivo_json:
        json.dump(relatorio, arquivo_json, indent=4, ensure_ascii=False)

    with open(RELATORIO_TXT, mode="w", encoding="utf-8") as arquivo_txt:
        arquivo_txt.write("========================================\n")
        arquivo_txt.write("RELATORIO DE DETECCAO DE PII\n")
        arquivo_txt.write("========================================\n")
        arquivo_txt.write(f"Data de execucao: {relatorio['data_execucao']}\n")
        arquivo_txt.write(f"Arquivo analisado: {relatorio['arquivo_analisado']}\n")
        arquivo_txt.write(f"Limite de deteccao: {LIMITE_DETECCAO:.0%}\n\n")

        if not resultado:
            arquivo_txt.write("Nenhuma coluna PII identificada.\n")
            return

        arquivo_txt.write("Colunas PII identificadas:\n\n")

        for item in resultado:
            arquivo_txt.write(f"Coluna: {item['coluna']}\n")
            arquivo_txt.write(f"Tipo PII: {item['tipo_pii']}\n")
            arquivo_txt.write(f"Valores analisados: {item['total_valores_analisados']}\n")
            arquivo_txt.write(f"Matches encontrados: {item['total_matches']}\n")
            arquivo_txt.write(f"Taxa de match: {item['taxa_match']:.2%}\n")
            arquivo_txt.write(f"Classificacao: {item['classificacao']}\n")
            arquivo_txt.write(f"Criterio: {item['criterio']}\n")
            arquivo_txt.write("----------------------------------------\n")


def main():
    linhas, colunas = carregar_csv(ARQUIVO_ENTRADA)
    resultado = calcular_pii_por_coluna(linhas, colunas)
    salvar_relatorios(resultado)

    print("========================================")
    print("SCAN DE PII CONCLUIDO")
    print("========================================")
    print(f"Arquivo analisado: {ARQUIVO_ENTRADA}")
    print(f"Relatorio TXT: {RELATORIO_TXT}")
    print(f"Relatorio JSON: {RELATORIO_JSON}")
    print("Colunas identificadas como PII:")

    for item in resultado:
        print(f"- {item['coluna']} => {item['tipo_pii']} ({item['taxa_match']:.2%})")


if __name__ == "__main__":
    main()