from aws_cdk import (
    Stack,
    RemovalPolicy,
    Duration,
    aws_s3 as s3,
    aws_s3_deployment as s3deploy,
    aws_iam as iam,
    aws_glue as glue,
    aws_stepfunctions as sfn,
    aws_stepfunctions_tasks as tasks,
    aws_sns as sns,
    aws_sns_subscriptions as subscriptions,
    aws_cloudwatch as cloudwatch,
    aws_cloudwatch_actions as cloudwatch_actions,
)
from constructs import Construct


class InfrastructureStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        scripts_bucket = s3.Bucket(
            self,
            "DataOpsScriptsBucket",
            versioned=True,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            removal_policy=RemovalPolicy.DESTROY,
            auto_delete_objects=True,
        )

        s3deploy.BucketDeployment(
            self,
            "DeployGlueScripts",
            sources=[s3deploy.Source.asset("../glue")],
            destination_bucket=scripts_bucket,
            destination_key_prefix="scripts/glue",
        )

        s3deploy.BucketDeployment(
            self,
            "DeployDbtScripts",
            sources=[s3deploy.Source.asset("../dbt")],
            destination_bucket=scripts_bucket,
            destination_key_prefix="scripts/dbt",
        )

        glue_role = iam.Role(
            self,
            "DataOpsGlueRole",
            assumed_by=iam.ServicePrincipal("glue.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSGlueServiceRole"
                )
            ],
        )

        scripts_bucket.grant_read(glue_role)

        self.criar_glue_job(
            nome="dataops-ingestao",
            script_path=f"s3://{scripts_bucket.bucket_name}/scripts/glue/ingestao.py",
            role_arn=glue_role.role_arn,
        )

        self.criar_glue_job(
            nome="dataops-transformacao-dbt",
            script_path=f"s3://{scripts_bucket.bucket_name}/scripts/dbt/transformacao_dbt.py",
            role_arn=glue_role.role_arn,
        )

        self.criar_glue_job(
            nome="dataops-atualizacao-views",
            script_path=f"s3://{scripts_bucket.bucket_name}/scripts/glue/atualizacao_views.py",
            role_arn=glue_role.role_arn,
        )

        etapa_ingestao = tasks.GlueStartJobRun(
            self,
            "Executar Ingestao",
            glue_job_name="dataops-ingestao",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        etapa_transformacao = tasks.GlueStartJobRun(
            self,
            "Executar Transformacao dbt",
            glue_job_name="dataops-transformacao-dbt",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        etapa_views = tasks.GlueStartJobRun(
            self,
            "Executar Atualizacao de Views",
            glue_job_name="dataops-atualizacao-views",
            integration_pattern=sfn.IntegrationPattern.RUN_JOB,
        )

        fluxo_pipeline = etapa_ingestao.next(etapa_transformacao).next(etapa_views)

        state_machine = sfn.StateMachine(
            self,
            "DataOpsStateMachine",
            state_machine_name="dataops-pipeline-stepfunctions",
            definition_body=sfn.DefinitionBody.from_chainable(fluxo_pipeline),
        )

        topico_alerta = sns.Topic(
            self,
            "DataOpsFailureTopic",
            topic_name="dataops-pipeline-failure-alerts",
            display_name="Alertas de Falha - DataOps Pipeline",
        )

        topico_alerta.add_subscription(
            subscriptions.EmailSubscription(
                "fabricio.dsantos@al.infnet.edu.br"
            )
        )

        alarme_falha_pipeline = cloudwatch.Alarm(
            self,
            "DataOpsStepFunctionsFailureAlarm",
            alarm_name="dataops-stepfunctions-failure-alarm",
            alarm_description="Alarme disparado quando a Step Function do pipeline DataOps falhar.",
            metric=state_machine.metric_failed(
                period=Duration.minutes(1),
                statistic="Sum",
            ),
            threshold=1,
            evaluation_periods=1,
            comparison_operator=cloudwatch.ComparisonOperator.GREATER_THAN_OR_EQUAL_TO_THRESHOLD,
            treat_missing_data=cloudwatch.TreatMissingData.NOT_BREACHING,
        )

        alarme_falha_pipeline.add_alarm_action(
            cloudwatch_actions.SnsAction(topico_alerta)
        )

    def criar_glue_job(self, nome: str, script_path: str, role_arn: str):
        glue.CfnJob(
            self,
            nome.replace("-", "").title(),
            name=nome,
            role=role_arn,
            command=glue.CfnJob.JobCommandProperty(
                name="pythonshell",
                python_version="3.9",
                script_location=script_path,
            ),
            glue_version="3.0",
            max_capacity=0.0625,
        )