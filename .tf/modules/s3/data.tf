########################################
# Module S3 - data
########################################

locals {
  bucket_name = "${lower(var.app_name)}-${var.bucket_name}-${var.env}"

  tags = merge(
    var.tags,
    tomap({
      "Name" = local.bucket_name
    })
  )
}

