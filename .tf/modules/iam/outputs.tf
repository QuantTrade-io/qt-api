########################################
# Module IAM - outputs
########################################
output "ses_user_name" {
  description = "Name of the user that can perform ses actions"
  value       = data.aws_iam_user.ses_user.user_name
}

