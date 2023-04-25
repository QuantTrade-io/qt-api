########################################
# Module S3 - outputs
########################################

output "s3_bucket_bucket_regional_domain_name" {
  description = "Domain Name of the S3 bucket that is created"
  value       = aws_s3_bucket.main.bucket_domain_name
}

output "s3_bucket_bucket_name" {
  description = "Name of the S3 bucket that is created"
  value       = aws_s3_bucket.main.id
}

output "s3_bucket_region" {
  description = "Name of the S3 bucket that is created"
  value       = aws_s3_bucket.main.region
}

output "s3_bucket_arn_access_path" {
  description = "ARN of the S3 bucket that is created"
  value       = "${aws_s3_bucket.main.arn}/*"
}

