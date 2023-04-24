########################################
# Common Meta Data
########################################
variable "env" {
  description = "The name of the environment."
  type        = string
}

variable "region" {
  description = "The region of the environment."
  type        = string
}

variable "role_name" {
  description = "The role of Terraform."
  type        = string
}

variable "profile_name" {
  description = "The profile name of the environment."
  type        = string
}

variable "application_name" {
  description = "The name of the application."
  type        = string
}

variable "app_name" {
  description = "The name of the application."
  type        = string
}

variable "reference_name" {
  description = "The shorter name of the application."
  type        = string
}

########################################
## Terraform Route53 - DNS && Routing
########################################
variable "no_reply_email" {
  description = "Email address that is used for no-reply stuff"
  type        = string
}

########################################
## Terraform Route53 - DNS && Routing
########################################
variable "route53_hosted_zone_name" {
  description = "Name of the hosted zone we want to retrieve"
  type        = string
}

variable "route53_hosted_zone_private" {
  description = "If the hosted zone we want to retrieve is private"
  type        = string
}
