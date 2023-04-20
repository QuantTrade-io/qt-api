########################################
# Common Meta Data
########################################
variable "env" {
  description = "The name of the environment."
  type        = string
}

variable "app_name" {
  description = "The name of the application."
  type        = string
}

variable "region" {
  description = "The AWS region this bucket should reside in."
  type        = string
}

variable "tags" {
  description = "A mapping of tags to assign to the resources."
  type        = map(any)
}

########################################
# Module SES - variables
########################################
variable "route53_zone_id" {
  description = "The zone ID of the Route53 resource"
  type        = string
}

variable "hosted_zone_name" {
  description = "Name of the hosted zone we want to retrieve"
  type        = string
}
