########################################
# Module Route53 - outputs
########################################
output "route53_zone_id" {
  description = "The zone ID of the Route53 resource"
  value       = data.aws_route53_zone.main.zone_id
}
