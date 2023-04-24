########################################
# Module IAM - main
########################################

data "aws_iam_user" "ses_user" {
  user_name = local.username
}

