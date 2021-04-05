module "kre-tnba-runtime" {
  source = "../../modules/kre-runtime"

  RUNTIME_NAME = "kre-email-tagger"
  CURRENT_ENVIRONMENT = var.CURRENT_ENVIRONMENT
}
