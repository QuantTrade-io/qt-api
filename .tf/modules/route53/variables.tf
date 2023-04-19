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
# Module Route53 - variables
########################################
variable "hosted_zone_name" {
  description = "Name of the hosted zone we want to retrieve"
  type        = string
}

variable "hosted_zone_private" {
  description = "If the hosted zone we want to retrieve is private"
  type        = string
}
