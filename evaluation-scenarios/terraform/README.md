# Controlled AWS Scenario Infrastructure

Terraform configuration for the controlled AWS scenarios will live in this directory.

Do **not** add or apply Terraform resources until all of the following are complete:

1. The exact resources and per-scenario tags are defined.
2. `CloudSentinelScenarioProvisioner` has a reviewed least-privilege policy.
3. The AWS Region, budget alarm, cleanup owner, and teardown process are recorded.
4. The user has configured a separate `cloudsentinel-provisioner` AWS CLI profile.
5. A reviewer approves the intended laboratory boundary.

The Terraform implementation must create only tagged, non-production resources and must support deterministic teardown. It must not create public Internet exposure for deliberately weak workloads.
