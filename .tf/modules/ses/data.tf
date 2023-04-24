########################################
# Module SES - data
########################################

locals {
  ses_iam_policy_name        = "QTAccessSES${var.env}"
  ses_iam_policy_description = "Policy for sending email on the ${var.env} environment"

  tags = merge(
    var.tags
  )
}
