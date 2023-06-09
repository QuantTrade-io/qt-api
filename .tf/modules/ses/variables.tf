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
variable "no_reply_email" {
  description = "Email address that is used for no-reply stuff"
  type        = string
}

variable "ses_user_name" {
  description = "Name of the user that is allowed to do SES stuff"
  type        = string
}
