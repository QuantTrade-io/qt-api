########################################
# Module IAM - data
########################################

locals {
  username = "${lower(var.reference_name)}-${var.env}-ses"

  tags = merge(
    var.tags
  )
}
