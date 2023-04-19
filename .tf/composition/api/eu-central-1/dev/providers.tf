########################################
# Provider to connect to AWS
#
# https://www.terraform.io/docs/providers/aws/
########################################

terraform {
  required_version = ">= 1.3.7"

  required_providers {
    aws = ">= 4.50.0, < 5.0"
  }

  backend "s3" {
    bucket         = "quanttrade-api-tfstate-dev"
    key            = "api/eu-central-1/dev/terraform.tfstate"
    region         = "eu-central-1"
    encrypt        = true
    dynamodb_table = "quanttrade-api-tfstate-lock-dev"
  }
}

provider "aws" {
  region = var.region
}

