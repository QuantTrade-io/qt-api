########################################
# Module SES - main
########################################
resource "aws_ses_domain_identity" "main" {
  domain = "example.com"
}

resource "aws_route53_record" "main" {
  zone_id = var.route53_zone_id
  name    = "_amazonses.${aws_ses_domain_identity.main.id}"
  type    = "TXT"
  ttl     = "600"
  records = [aws_ses_domain_identity.main.verification_token]
}

resource "aws_ses_domain_identity_verification" "example_verification" {
  domain = aws_ses_domain_identity.main.id

  depends_on = [aws_route53_record.main]
}
