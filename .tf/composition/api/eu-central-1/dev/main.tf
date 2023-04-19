########################################
# QuantTrade API composition
########################################

########################################
## Terraform SES - Mail Server
########################################
module "ses_mail_server" {
  source = "../../../../modules/ses"

  ## Common Meta Data ##
  env      = var.env
  app_name = var.app_name
  tags     = local.tags
  region   = var.region
}
