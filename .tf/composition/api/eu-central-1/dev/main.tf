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

###############################################
## Terraform Route53 - DNS & Routing
###############################################
module "route53_dns_routing" {
  source = "../../../../modules/route53"

  ## Common Meta Data ##
  env      = var.env
  app_name = var.app_name
  tags     = local.tags
  region   = var.region

  ## S3 variables ##
  hosted_zone_name    = var.route53_hosted_zone_name
  hosted_zone_private = var.route53_hosted_zone_private
}
