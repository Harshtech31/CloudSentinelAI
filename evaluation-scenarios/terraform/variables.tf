variable "aws_region" {
  description = "AWS Region used exclusively for the controlled evaluation lab."
  type        = string
}

variable "aws_profile" {
  description = "Local AWS CLI profile for the reviewed provisioner identity."
  type        = string
  default     = "cloudsentinel-provisioner"
}

variable "owner" {
  description = "Named owner responsible for cleanup."
  type        = string
  default     = "Harshith"
}

variable "cleanup_date" {
  description = "ISO-8601 date by which all lab resources must be deleted."
  type        = string

  validation {
    condition     = can(regex("^\\d{4}-\\d{2}-\\d{2}$", var.cleanup_date))
    error_message = "cleanup_date must use YYYY-MM-DD format."
  }
}

variable "enable_s1_public_control_scenario" {
  description = "Temporarily weaken only the empty S1 test bucket's public-access controls and add an object-read-only public policy."
  type        = bool
  default     = false
}

variable "enable_s2_bucket_wildcard_scenario" {
  description = "Temporarily grant s3:* only on the empty S1 test bucket to the dedicated S2 test role."
  type        = bool
  default     = false
}

variable "enable_s4_disabled_trail_scenario" {
  description = "Create a dedicated, disabled CloudTrail test trail with a private encrypted log bucket."
  type        = bool
  default     = false
}

variable "scenario_suffix" {
  description = "Lowercase account-local suffix for deterministic test resource names."
  type        = string
  default     = "lab"

  validation {
    condition     = can(regex("^[a-z0-9-]+$", var.scenario_suffix))
    error_message = "scenario_suffix may contain only lowercase letters, numbers, and hyphens."
  }
}
