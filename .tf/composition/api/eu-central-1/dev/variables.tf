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

########################################
## Terraform S3 Bucket - Public Assets
########################################
variable "s3_bucket_public_assets_name" {
  description = "Name of the S3 bucket where public assets are uploaded manually"
  type        = string
}


variable "s3_bucket_public_assets_acl" {
  description = "ACL of the S3 bucket where public assets are uploaded manually"
  type        = string
}

variable "s3_bucket_public_assets_force_destroy" {
  description = "Force destory the AWS S3 bucket"
  type        = bool
}

variable "s3_bucket_public_assets_versioning_enabled" {
  description = "Enable versioning for this S3 bucket"
  type        = string
}

variable "s3_bucket_public_assets_block_public_policy" {
  description = "Whether Amazon S3 should block public bucket policies for this bucket."
  type        = bool
}

variable "s3_bucket_public_assets_block_public_acls" {
  description = "Whether Amazon S3 should ignore public ACLs for this bucket."
  type        = bool
}

variable "s3_bucket_public_assets_ignore_public_acls" {
  description = "Whether Amazon S3 should ignore public ACLs for this bucket."
  type        = bool
}

variable "s3_bucket_public_assets_restrict_public_buckets" {
  description = "Whether Amazon S3 should restrict public bucket policies for this bucket."
  type        = bool
}

