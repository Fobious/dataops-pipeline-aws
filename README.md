# DataOps Pipeline AWS

Projeto desenvolvido para a disciplina **DataOps: Governança de Orquestração de Pipelines na Nuvem**.

## Objetivo

Implementar uma esteira DataOps na AWS para automatizar o versionamento, deploy, orquestração, monitoramento e alerta de falhas em um pipeline de dados.

## Arquitetura prevista

O projeto será composto por:

- GitHub para versionamento do código;
- AWS CodePipeline e CodeBuild para CI/CD;
- Amazon S3 para armazenamento dos scripts;
- AWS Glue para execução dos jobs de dados;
- AWS Step Functions para orquestração do pipeline;
- Amazon CloudWatch para monitoramento;
- Amazon SNS para envio de alertas por e-mail em caso de falha.

## Fluxo esperado

1. Desenvolvedor realiza commit na branch `main`;
2. CodePipeline identifica a alteração automaticamente;
3. CodeBuild executa o processo de build/deploy;
4. Scripts são atualizados no S3;
5. Infraestrutura é aplicada via CDK;
6. Step Functions orquestra as etapas:
   - Ingestão;
   - Transformação dbt;
   - Atualização de Views;
7. CloudWatch monitora a execução;
8. Em caso de falha, SNS envia alerta por e-mail.

## Entregáveis

- Link do repositório;
- Diagrama do pipeline CI/CD;
- Print do e-mail de alerta recebido após falha simulada.