# Scenario Provisioner Policy

`CloudSentinelScenarioProvisionerPolicy.template.json` is the reviewed policy template for the IAM user named `CloudSentinelScenarioProvisioner`.

## Current scope

The policy is intentionally limited to the initial Terraform baseline in `../terraform/`:

- S1: a named CloudSentinel evaluation S3 bucket with encryption and public-access protections;
- S2/S5: a named test IAM role and its inline policy, limited to the evaluation bucket;
- S3: tagged VPC and security-group resources in `ap-south-2` only.

It does **not** permit EC2 instances, NAT gateways, Internet gateways, public IPs, RDS, secret values, CloudTrail state changes, arbitrary IAM administration, or access to unrelated AWS Regions.

## Before attaching the policy

1. Open **IAM → Policies → Create policy → JSON**.
2. Paste the policy template and use the IAM policy validator.
3. Confirm there are zero validation errors.
4. Name the policy `CloudSentinelScenarioProvisionerPolicy`.
5. Attach it only to `CloudSentinelScenarioProvisioner`.
6. Do not create an access key until the policy is attached and the Terraform plan is ready for review.

## Important limitation

The policy is a Terraform-baseline policy, not a general cloud-administration policy. If Terraform later reports an `AccessDenied` error, do not attach a broad managed policy. Record the exact denied action and resource, then extend this template narrowly and revalidate it.
