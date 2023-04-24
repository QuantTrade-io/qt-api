########################################
# Module SES - main
########################################

resource "aws_ses_email_identity" "main" {
  email = var.no_reply_email
}

data "template_file" "ses_send_email_policy" {
  template = file("./templates/ses/ses-access-policy.json")

  vars = {
    SES_ARN = aws_ses_email_identity.main.arn
  }
}

resource "aws_iam_policy" "ses_send_email_policy" {
  name        = local.ses_iam_policy_name
  description = local.ses_iam_policy_description
  policy      = data.template_file.ses_send_email_policy.rendered
}

resource "aws_iam_user_policy_attachment" "ses_user_policy_attachement" {
  user       = var.ses_user_name
  policy_arn = aws_iam_policy.ses_send_email_policy.arn
}

