import datetime


def main():
    print("========================================")
    print("INICIANDO ETAPA DE INGESTAO")
    print("========================================")

    data_execucao = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    print(f"Data de execucao: {data_execucao}")
    print("Simulando leitura de dados de origem...")
    print("Simulando gravacao dos dados brutos no Data Lake...")
    print("Etapa de ingestao concluida com sucesso.")


if __name__ == "__main__":
    main()