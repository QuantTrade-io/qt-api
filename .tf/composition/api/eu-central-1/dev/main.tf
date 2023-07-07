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

###############################################
## Terraform S3 - Public assets
###############################################
module "s3_public_assets" {
  source = "../../../../modules/s3"

  ## Common Meta Data ##
  env      = var.env
  app_name = var.app_name
  tags     = local.tags
  region   = var.region

  ## S3 variables ##
  bucket_name             = var.s3_bucket_public_assets_name
  bucket_acl              = var.s3_bucket_public_assets_acl
  force_destroy           = var.s3_bucket_public_assets_force_destroy
  versioning_enabled      = var.s3_bucket_public_assets_versioning_enabled
  block_public_policy     = var.s3_bucket_public_assets_block_public_policy
  block_public_acls       = var.s3_bucket_public_assets_block_public_acls
  ignore_public_acls      = var.s3_bucket_public_assets_ignore_public_acls
  restrict_public_buckets = var.s3_bucket_public_assets_restrict_public_buckets
  create_s3_public_policy = var.s3_bucket_public_assets_create_s3_public_policy
}

###############################################
## Terraform S3 - Private assets
###############################################
module "s3_private_assets" {
  source = "../../../../modules/s3"

  ## Common Meta Data ##
  env      = var.env
  app_name = var.app_name
  tags     = local.tags
  region   = var.region

  ## S3 variables ##
  bucket_name             = var.s3_bucket_private_assets_name
  bucket_acl              = var.s3_bucket_private_assets_acl
  force_destroy           = var.s3_bucket_private_assets_force_destroy
  versioning_enabled      = var.s3_bucket_private_assets_versioning_enabled
  block_public_policy     = var.s3_bucket_private_assets_block_public_policy
  block_public_acls       = var.s3_bucket_private_assets_block_public_acls
  ignore_public_acls      = var.s3_bucket_private_assets_ignore_public_acls
  restrict_public_buckets = var.s3_bucket_private_assets_restrict_public_buckets
  create_s3_public_policy = var.s3_bucket_private_assets_create_s3_public_policy
}