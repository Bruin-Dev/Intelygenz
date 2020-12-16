resource "aws_iam_role" "rest-api-data-collector-role" {
  name                  = "rest-api-data-collector-${var.CURRENT_ENVIRONMENT}-role"
  assume_role_policy    = file("${path.module}/policies/lambda-data-collector-role.json")
  force_detach_policies = true
}

resource "aws_iam_role_policy" "rest-api-data-collector-role-policy" {
  name   = "lambda-data-collector-role-policy-${var.CURRENT_ENVIRONMENT}"
  policy = file("${path.module}/policies/lambda-data-collector-role-policy.json")
  role   = aws_iam_role.rest-api-data-collector-role.id
}

resource "aws_security_group" "data_collector_lambda_sg" {
  name        = local.rest-api-data-collector-lambda-security_group-name
  vpc_id      = data.aws_vpc.mettel-automation-vpc.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name = local.rest-api-data-collector-lambda-security_group-name
    Environment = var.CURRENT_ENVIRONMENT
    Project = local.project_name
  }
}

resource "aws_lambda_permission" "data_collector_permission" {
  statement_id  = "AllowAPIGatewayInvoke"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.data_collector.arn
  principal     = "apigateway.amazonaws.com"

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn =  "${aws_apigatewayv2_api.data-collector-api-gateway.execution_arn}/*/*/csv"
}

resource "aws_lambda_permission" "data_collector_permission_api" {
  statement_id  = "AllowAPIGatewayInvoke-api"
  action        = "lambda:InvokeFunction"
  function_name = aws_lambda_function.data_collector.arn
  principal     = "apigateway.amazonaws.com"

  # The /*/*/* part allows invocation from any stage, method and resource path
  # within API Gateway REST API.
  source_arn =  "${aws_apigatewayv2_api.data-collector-api-gateway.execution_arn}/*/*/api/{proxy+}"
}

resource "aws_lambda_function" "data_collector" {
  filename      = "${path.module}/lambdas/rest-api-data-collector/rest-api-data-collector.zip"
  function_name = local.rest-api-data-collector-lambda-function_name
  role          = aws_iam_role.rest-api-data-collector-role.arn
  handler       = "main.handler"
  source_code_hash = filebase64sha256("${path.module}/lambdas/rest-api-data-collector/main.py")

  runtime = "python3.8"

  vpc_config {
    subnet_ids         = data.aws_subnet_ids.mettel-automation-private-subnets.ids
    security_group_ids = [aws_security_group.data_collector_lambda_sg.id]
  }

  environment {
    variables = {
      AUTH_TOKEN         = var.REST_API_DATA_COLLECTOR_AUTH_TOKEN
      MONGODB_COLLECTION = var.REST_API_DATA_COLLECTOR_MONGODB_COLLECTION
      MONGODB_DATABASE   = var.REST_API_DATA_COLLECTOR_MONGODB_DATABASE
      MONGODB_HOST       = aws_docdb_cluster.data_collector_docdb_cluster.endpoint
      MONGODB_USERNAME   = var.DOCDB_CLUSTER_MASTER_USERNAME
      MONGODB_PASSWORD   = var.DOCDB_CLUSTER_MASTER_PASSWORD
      MONGODB_QUERYSTRING = var.REST_API_DATA_COLLECTOR_MONGODB_QUERYSTRING
    }
  }

  depends_on = [null_resource.add_docdb_pem_to_zip_data_collector_lambda,
                aws_docdb_cluster.data_collector_docdb_cluster,
                aws_docdb_cluster_instance.data_collector_docdb_instance]
}
