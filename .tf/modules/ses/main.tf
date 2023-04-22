########################################
# Module SES - main
########################################

resource "aws_ses_email_identity" "main" {
  email = "no-reply@quanttrade.io"
}

