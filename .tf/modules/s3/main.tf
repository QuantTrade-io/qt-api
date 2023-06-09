########################################
# Module S3 - main
########################################
resource "aws_s3_bucket" "main" {
  bucket        = local.bucket_name
  tags          = local.tags
  force_destroy = var.force_destroy
}

resource "aws_s3_bucket_public_access_block" "main" {
  bucket = aws_s3_bucket.main.id

  ## s3 bucket public access block ##
  block_public_policy     = var.block_public_policy
  block_public_acls       = var.block_public_acls
  ignore_public_acls      = var.ignore_public_acls
  restrict_public_buckets = var.restrict_public_buckets
}

resource "aws_s3_bucket_versioning" "main" {
  bucket = aws_s3_bucket.main.id
  versioning_configuration {
    status = var.versioning_enabled
  }
}

resource "aws_s3_bucket_ownership_controls" "main" {
  bucket = aws_s3_bucket.main.id
  rule {
    object_ownership = "BucketOwnerPreferred"
  }
}

resource "aws_s3_bucket_acl" "main" {
  depends_on = [
    aws_s3_bucket_ownership_controls.main,
    aws_s3_bucket_public_access_block.main,
  ]

  bucket = aws_s3_bucket.main.id
  acl    = var.bucket_acl
}

data "template_file" "s3_send_email_policy" {
  template = file("./templates/s3/s3-access-policy.json")

  vars = {
    S3_ARN = aws_s3_bucket.main.arn
  }
}

resource "aws_s3_bucket_policy" "allow_access_from_another_account" {
  count  = var.create_s3_public_policy ? 1 : 0
  bucket = aws_s3_bucket.main.id
  policy = data.template_file.s3_send_email_policy.rendered
}

