# server

## Setup

### Prerequisites
- [OpenAI API key](https://openai.com/api)
- [AWS CLI](https://docs.localstack.cloud/user-guide/integrations/aws-cli/#localstack-aws-cli-awslocal)
- [AWS SAM CLI](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/install-sam-cli.html#install-sam-cli-instructions)
- [LocalStack](https://github.com/localstack/localstack)

Save secrets:

```bash
awslocal --region ap-northeast-1 secretsmanager create-secret --name tokyo-landprice-rag-localstack --secret-string file://secret.localstack.json
```

Check if the secrets have been saved:

```bash
awslocal --region ap-northeast-1 secretsmanager describe-secret --secret-id geoguess-lite-localstack
```

You can delete the secrets by running the following command:

```bash
awslocal --region ap-northeast-1 secretsmanager delete-secret --secret-id geoguess-lite-localstack --force-delete-without-recovery
```

Build SAM:

```bash
sam build --use-container
```

Run SAM:

```bash
sam local start-api --region us-east-1 --docker-network <localstack-network-id> --port 3001 --parameter-overrides Environment=localstack
```
