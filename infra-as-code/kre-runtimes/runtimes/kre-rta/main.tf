module "kre-rta-runtime" {
  source = "../../modules/kre-runtime"

  RUNTIME_NAME = "kre-rta"
  CURRENT_ENVIRONMENT = var.CURRENT_ENVIRONMENT
}
