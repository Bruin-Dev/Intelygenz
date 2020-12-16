output "api_gateway_endpoint_data_collector" {
  description = "API Gateway endpoint for call data-collector lambda"
  value       = aws_apigatewayv2_api.data-collector-api-gateway.api_endpoint
}