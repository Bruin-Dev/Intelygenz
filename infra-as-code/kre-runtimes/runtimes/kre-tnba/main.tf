module "kre-tnba-runtime" {
  source = "../../modules/kre-runtime"

  RUNTIME_NAME = "kre-tnba"
  CURRENT_ENVIRONMENT = var.CURRENT_ENVIRONMENT
}
