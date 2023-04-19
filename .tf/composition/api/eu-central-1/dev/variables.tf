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
