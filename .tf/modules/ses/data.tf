########################################
# Module SES - data
########################################

locals {
    ses_role_policy_name = "${lower(var.app_name)}-${var.env}-ses-mail"
    ses_role_policy_path = "/"
    ses_role_policy_description = "Allow sending email via SES"

    ses_identity_policy_name = ""

  tags = merge(
    var.tags
  )
}
