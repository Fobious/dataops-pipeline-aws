# aqui configuração 1.2 de erro para nenhum erro ser aceito, ou seja, se houver algum teste com erro o quality gate reprova o pipeline.

import json
import sys
from pathlib import Path


LIMITE_ACEITAVEL_ERRO = 0.0

run_results_path = Path("target/run_results.json")

if not run_results_path.exists():
    print("ERRO: Arquivo target/run_results.json não encontrado.")
    print("Execute primeiro o comando: dbt test")
    sys.exit(1)

with open(run_results_path, "r", encoding="utf-8") as file:
    run_results = json.load(file)

testes = [
    resultado
    for resultado in run_results.get("results", [])
    if resultado.get("unique_id", "").startswith("test.")
]

total_testes = len(testes)

testes_com_erro = [
    teste
    for teste in testes
    if teste.get("status") in ["fail", "error"]
]

total_erros = len(testes_com_erro)
taxa_erro = total_erros / total_testes if total_testes > 0 else 1

print("========================================")
print("DATA QUALITY GATE - DBT")
print("========================================")
print(f"Total de testes executados: {total_testes}")
print(f"Total de testes com erro: {total_erros}")
print(f"Taxa de erro: {taxa_erro:.2%}")
print(f"Limite aceitavel: {LIMITE_ACEITAVEL_ERRO:.2%}")

if taxa_erro > LIMITE_ACEITAVEL_ERRO:
    print("RESULTADO: QUALITY GATE REPROVADO")
    print("O pipeline deve ser interrompido.")
    sys.exit(1)

print("RESULTADO: QUALITY GATE APROVADO")
print("O pipeline pode continuar.")
sys.exit(0)