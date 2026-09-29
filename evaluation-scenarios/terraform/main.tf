provider "aws" {
  region  = var.aws_region
  profile = var.aws_profile

  default_tags {
    tags = {
      Project     = "CloudSentinel"
      Environment = "Evaluation"
      Owner       = var.owner
      CleanupDate = var.cleanup_date
      ManagedBy   = "Terraform"
    }
  }
}

data "aws_caller_identity" "current" {}

locals {
  bucket_name = "cloudsentinel-eval-${data.aws_caller_identity.current.account_id}-${var.scenario_suffix}-s1"
}

# S1 baseline: a test-only bucket that retains all public-access protections.
# A future approved scenario may assess a weakened control without placing data
# or a workload on the public Internet.
resource "aws_s3_bucket" "scenario_s1" {
  bucket        = local.bucket_name
  force_destroy = false

  tags = {
    Scenario       = "S1"
    SafetyBoundary = "NoPublicData"
  }
}

resource "aws_s3_bucket_public_access_block" "scenario_s1" {
  bucket = aws_s3_bucket.scenario_s1.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "scenario_s1" {
  bucket = aws_s3_bucket.scenario_s1.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "AES256"
    }
  }
}

# S2/S5 baseline: a dedicated test role whose permissions are constrained to
# the test bucket. No production resource or secret is referenced.
data "aws_iam_policy_document" "scenario_role_trust" {
  statement {
    effect  = "Allow"
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["ec2.amazonaws.com"]
    }
  }
}

resource "aws_iam_role" "scenario_s2_s5" {
  name               = "cloudsentinel-eval-${var.scenario_suffix}-s2-s5"
  assume_role_policy = data.aws_iam_policy_document.scenario_role_trust.json

  tags = {
    Scenario       = "S2,S5"
    SafetyBoundary = "TestBucketOnly"
  }
}

data "aws_iam_policy_document" "scenario_role_permissions" {
  statement {
    sid     = "TestBucketOnly"
    effect  = "Allow"
    actions = ["s3:ListBucket", "s3:GetObject"]
    resources = [
      aws_s3_bucket.scenario_s1.arn,
      "${aws_s3_bucket.scenario_s1.arn}/*"
    ]
  }
}

resource "aws_iam_role_policy" "scenario_s2_s5" {
  name   = "cloudsentinel-eval-test-bucket-access"
  role   = aws_iam_role.scenario_s2_s5.id
  policy = data.aws_iam_policy_document.scenario_role_permissions.json
}

# S3 baseline: an isolated VPC with no Internet gateway, route tables, or
# compute resources. The broad ingress rule is limited to an unused port and
# exists only as a configuration-analysis fixture; it creates no public workload.
resource "aws_vpc" "scenario_s3" {
  cidr_block           = "10.200.0.0/16"
  enable_dns_hostnames = false
  enable_dns_support   = true

  tags = {
    Name           = "cloudsentinel-eval-${var.scenario_suffix}-s3"
    Scenario       = "S3"
    SafetyBoundary = "NoInternetGatewayNoWorkload"
  }
}

resource "aws_security_group" "scenario_s3" {
  name        = "cloudsentinel-eval-${var.scenario_suffix}-s3"
  description = "Configuration-analysis fixture with no attached workload"
  vpc_id      = aws_vpc.scenario_s3.id

  ingress {
    description = "Fixture-only broad ingress on an unused port; no route or workload exists"
    from_port   = 8443
    to_port     = 8443
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress = []

  tags = {
    Scenario       = "S3"
    SafetyBoundary = "NoPublicWorkload"
  }
}
