########################################
# Module SES - main
########################################
resource "aws_ses_domain_identity" "main" {
  domain = var.hosted_zone_name
}

resource "aws_route53_record" "main" {
  zone_id = var.route53_zone_id
  name    = "_amazonses.${aws_ses_domain_identity.main.id}"
  type    = "TXT"
  ttl     = "600"
  records = [aws_ses_domain_identity.main.verification_token]
}

resource "aws_ses_domain_identity_verification" "main" {
  domain = aws_ses_domain_identity.main.id

  depends_on = [aws_route53_record.main]
}

resource "aws_ses_email_identity" "main" {
  email = "noreply@quanttrade.io"
}

resource "aws_ses_domain_mail_from" "main" {
  domain           = aws_ses_email_identity.main.email
  mail_from_domain = "mail.quanttrade.io"
}

resource "aws_route53_record" "example_ses_domain_mail_from_mx" {
  zone_id = var.route53_zone_id
  name    = aws_ses_domain_mail_from.main.mail_from_domain
  type    = "MX"
  ttl     = "600"
  records = ["10 feedback-smtp.eu-central-1.amazonses.com"]
}

resource "aws_route53_record" "example_ses_domain_mail_from_txt" {
  zone_id = var.route53_zone_id
  name    = aws_ses_domain_mail_from.main.mail_from_domain
  type    = "TXT"
  ttl     = "600"
  records = ["v=spf1 include:amazonses.com -all"]
}
