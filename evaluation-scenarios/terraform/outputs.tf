output "evaluation_account_id" {
  description = "AWS account that Terraform would target after explicit approval."
  value       = data.aws_caller_identity.current.account_id
}

output "scenario_s1_bucket_name" {
  description = "Test-only S1 bucket name."
  value       = aws_s3_bucket.scenario_s1.bucket
}

output "scenario_s2_s5_role_arn" {
  description = "Dedicated test role ARN for S2/S5 metadata collection."
  value       = aws_iam_role.scenario_s2_s5.arn
}

output "scenario_s3_security_group_id" {
  description = "Unattached S3 configuration-analysis security group ID."
  value       = aws_security_group.scenario_s3.id
}
