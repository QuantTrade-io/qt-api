########################################
# Module Route53 - main
########################################

data "aws_route53_zone" "main" {
  name         = var.hosted_zone_name
  private_zone = var.hosted_zone_private
}
