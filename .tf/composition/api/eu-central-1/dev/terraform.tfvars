########################################
# Environment setting
########################################
region           = "eu-central-1"
role_name        = "Admin"
profile_name     = "quanttrade-api"
env              = "dev"
application_name = "quanttrade-api"
app_name         = "quanttrade-api"
reference_name   = "qt-api"

## Global data ##
no_reply_email = "no-reply@quanttrade.io"

## Route53 - DNS && Routing ##
route53_hosted_zone_name    = "quanttrade.io"
route53_hosted_zone_private = false

## S3 bucket - Public Assets ##
s3_bucket_public_assets_name                    = "public-assets"
s3_bucket_public_assets_acl                     = "public-read"
s3_bucket_public_assets_force_destroy           = false
s3_bucket_public_assets_versioning_enabled      = "Disabled"
s3_bucket_public_assets_block_public_policy     = false
s3_bucket_public_assets_block_public_acls       = false
s3_bucket_public_assets_ignore_public_acls      = false
s3_bucket_public_assets_restrict_public_buckets = false
s3_bucket_public_assets_create_s3_public_policy = true

## S3 bucket - Private Assets ##
s3_bucket_private_assets_name                    = "private-assets"
s3_bucket_private_assets_acl                     = "private"
s3_bucket_private_assets_force_destroy           = false
s3_bucket_private_assets_versioning_enabled      = "Disabled"
s3_bucket_private_assets_block_public_policy     = true
s3_bucket_private_assets_block_public_acls       = true
s3_bucket_private_assets_ignore_public_acls      = true
s3_bucket_private_assets_restrict_public_buckets = true
s3_bucket_private_assets_create_s3_public_policy = false