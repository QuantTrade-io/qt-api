#######################################
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
# Module S3 Bucket - variables
########################################
variable "bucket_name" {
  description = "Suffix for the S3 bucket name"
  type        = string
}


variable "bucket_acl" {
  description = "ACL for the S3 bucket name"
  type        = string
}

variable "force_destroy" {
  description = "Force destory the AWS S3 bucket"
  type        = bool
}

variable "versioning_enabled" {
  description = "Enable versioning for this S3 bucket"
  type        = string
}

variable "block_public_policy" {
  description = "Whether Amazon S3 should block public bucket policies for this bucket."
  type        = bool
}

variable "block_public_acls" {
  description = "Whether Amazon S3 should ignore public ACLs for this bucket."
  type        = bool
}

variable "ignore_public_acls" {
  description = "Whether Amazon S3 should ignore public ACLs for this bucket."
  type        = bool
}

variable "restrict_public_buckets" {
  description = "Whether Amazon S3 should restrict public bucket policies for this bucket."
  type        = bool
}

