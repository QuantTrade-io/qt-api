########################################
# Data sources
########################################

locals {
  # Common Meta Data
  tags = {
    Region      = var.region
    Application = var.application_name
    ManagedBy   = "Terraform"
    RoleName    = var.role_name
  }
}

# Current cccount ID
data "aws_caller_identity" "current" {}
