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
