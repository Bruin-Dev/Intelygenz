resource "aws_apigatewayv2_api" "data-collector-api-gateway" {
  name        = local.api-gateway-data-collector
  protocol_type = "HTTP"
}

resource "aws_apigatewayv2_integration" "data-collector-api-gateway" {
  api_id                    = aws_apigatewayv2_api.data-collector-api-gateway.id

  integration_type          = "AWS_PROXY"
  connection_type           = "INTERNET"
  description               = "Connection with lambda ${aws_lambda_function.data_collector.function_name}"
  integration_method        = "POST"
  integration_uri           = aws_lambda_function.data_collector.invoke_arn
}

resource "aws_apigatewayv2_route" "data-collector-route-csv" {
  authorization_type  = "NONE"
  api_id              = aws_apigatewayv2_api.data-collector-api-gateway.id
  route_key           = "GET /csv"
  target              = "integrations/${aws_apigatewayv2_integration.data-collector-api-gateway.id}"
}

resource "aws_apigatewayv2_route" "data-collector-route-api" {
  authorization_type  = "NONE"
  api_id              = aws_apigatewayv2_api.data-collector-api-gateway.id
  route_key           = "ANY /api/{proxy+}"
  target              = "integrations/${aws_apigatewayv2_integration.data-collector-api-gateway.id}"
}

resource "aws_apigatewayv2_deployment" "data-collector-route-api-deployment" {
  api_id      = aws_apigatewayv2_route.data-collector-route-api.api_id
  description = "Deployment of ${aws_apigatewayv2_route.data-collector-route-api.api_id}"

  lifecycle {
    create_before_destroy = true
  }
}

resource "aws_apigatewayv2_stage" "data-collector-default-stage" {
  api_id        = aws_apigatewayv2_api.data-collector-api-gateway.id
  name          = "$default"
  deployment_id = aws_apigatewayv2_deployment.data-collector-route-api-deployment.id

  depends_on = [aws_apigatewayv2_api.data-collector-api-gateway,
                aws_apigatewayv2_integration.data-collector-api-gateway,
                aws_apigatewayv2_route.data-collector-route-api,
                aws_apigatewayv2_deployment.data-collector-route-api-deployment]

}