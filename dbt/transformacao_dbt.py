import datetime


def main():
    print("========================================")
    print("INICIANDO ETAPA DE TRANSFORMACAO DBT")
    print("========================================")

    data_execucao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"Data de execucao: {data_execucao}")
    print("Simulando execucao de modelos dbt...")
    print("Simulando tratamento, limpeza e modelagem dos dados...")
    print("Etapa de transformacao dbt concluida com sucesso.")


if __name__ == "__main__":
    main()