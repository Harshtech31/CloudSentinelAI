# Controlled Cloud Deployment Runbook

## Status

**Do not apply Terraform yet.** This runbook becomes active only after the region is selected, the provisioner policy template is reviewed and completed, and `CloudSentinelScenarioProvisioner` receives the approved policy.

## Baseline resources

The initial Terraform configuration is intentionally limited to:

- S1: an empty, encrypted S3 test bucket with all public-access protections enabled;
- S2/S5: a test IAM role limited to the test bucket;
- S3: an isolated VPC and unattached security group with no Internet gateway, route, subnet, public IP, or compute workload.

It does not create EC2 instances, RDS instances, NAT gateways, public IPs, Internet gateways, secret values, CloudTrail state changes, or an SSRF-capable application.

## Preconditions

1. Use the approved evaluation Region `ap-south-2` (Hyderabad) and record it in the evaluation evidence.
2. Set a $2 and $5 AWS Budget alert.
3. Validate `iam/CloudSentinelScenarioProvisionerPolicy.template.json` in the IAM console before attaching it.
4. Attach the reviewed policy only to `CloudSentinelScenarioProvisioner`.
5. Create an access key for that user only after the policy is attached; configure it as the local `cloudsentinel-provisioner` profile.
6. Copy `terraform.tfvars.example` to untracked `terraform.tfvars` and set a cleanup date.
7. Run `terraform plan` and review every proposed resource before any apply.

## Prohibited actions

- Do not use root credentials with Terraform.
- Do not attach `AdministratorAccess`, `PowerUserAccess`, or broad managed policies to the provisioner.
- Do not apply while a public workload, production data, or production credential could be involved.
- Do not commit `terraform.tfvars`, state files, CLI credentials, plan files, or evidence artifacts.

## Cleanup

After any approved deployment, run the reviewed Terraform destroy process, confirm the S3 bucket is empty, and verify that the VPC, security group, IAM role, and policy are removed. Record cleanup confirmation in the local evidence directory.
