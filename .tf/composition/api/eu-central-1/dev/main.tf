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

  ## Route53 variables ##
  no_reply_email = var.no_reply_email
  ses_user_name  = module.iam_users_roles_permissions.ses_user_name
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

  ## Route53 variables ##
  hosted_zone_name    = var.route53_hosted_zone_name
  hosted_zone_private = var.route53_hosted_zone_private
}

###############################################
## Terraform IAM - Users, roles & permissions
###############################################
module "iam_users_roles_permissions" {
  source = "../../../../modules/iam"

  ## Common Meta Data ##
  env            = var.env
  app_name       = var.app_name
  tags           = local.tags
  region         = var.region
  reference_name = var.reference_name
}
