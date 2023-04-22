########################################
# Module SES - main
########################################

resource "aws_ses_email_identity" "main" {
  email = "no-reply@quanttrade.io"
}

resource "aws_iam_policy" "ses_role_policy" {
  name        = local.ses_role_policy_name
  path        = local.ses_role_policy_path
  description = local.ses_role_policy_description
  policy      = file("./templates/ses/ses-role.json")
}

# Attaches a Managed IAM Policy to an IAM user
resource "aws_iam_user_policy_attachment" "user_policy" {
  user       = "qt-joris"
  policy_arn = aws_iam_policy.ses_role_policy.arn
}
