# CloudSentinel Controlled Evaluation Scenarios

This directory is the source of truth for the controlled AWS evaluation catalogue described in `cloudsentinel-thesis/ieee-paper/paper.tex`.

## Safety boundary

- Use only an authorised, non-production AWS account.
- Use synthetic or non-sensitive data only; never store credentials in this repository.
- Apply project, owner, scenario, and cleanup-date tags to every test resource.
- Configure budget alarms and a documented teardown procedure before deployment.
- Keep deliberately weak configurations within the approved laboratory boundary; do not expose vulnerable workloads to the public Internet.
- Do not run Scenario S6 against real applications or production metadata services.

## Contents

- `catalog.json` — scenario metadata and test boundaries.
- `ground-truth/catalog.json` — expected findings, negative controls, candidate-path expectations, and evidence requirements.
- `scripts/validate_catalog.py` — dependency-free validation of the two JSON files.
- `scripts/run_local_scenarios.py` — safe in-memory fixture validation using the backend attack-graph classes; it never calls AWS.
- `scripts/collect_baseline_evidence.py` — a read-only evaluator for the deployed S3, IAM, VPC, and security-group baseline; it does not list or read S3 objects, retrieve secrets, or modify AWS.
- `tests/` — automated tests for local fixtures and the baseline evaluator's path-precondition logic.
- `terraform/` — reviewed, tagged, non-production baseline infrastructure. Do not apply it before following `runbooks/cloud-deployment.md`.
- `iam/` — policy templates for reviewed scenario identities; templates are not ready to attach until all placeholders are replaced and validated in the IAM console.
- `runbooks/` — deployment and cleanup prerequisites.
- `evidence/` — local, untracked-by-convention location for execution records. Do not place secrets or sensitive data here.

## Scenario lifecycle

1. Review and approve a scenario's ground truth before deployment.
2. Record the deployed configuration and tool versions outside the repository or in a sanitised evidence record.
3. Run CloudSentinel and each selected baseline using the same authorised scope.
4. Preserve sanitised scan output, graph evidence, timing records, and cleanup verification.
5. Classify candidate paths as exact, partial, or invalid according to the frozen ground truth.
6. Destroy all test resources and verify cleanup.

## Validation

Run from the repository root:

```bash
python3 evaluation-scenarios/scripts/validate_catalog.py
python3 evaluation-scenarios/scripts/run_local_scenarios.py
python3 -m pytest evaluation-scenarios/tests
```

This validates catalogue structure and local evaluator logic only. It does not create AWS resources or assess live cloud security.

To run the approved read-only baseline evaluator, create the ignored local environment once, then write only sanitised output to `evidence/`:

```bash
python3 -m venv evaluation-scenarios/.venv
evaluation-scenarios/.venv/bin/python -m pip install 'boto3>=1.34.0,<2.0.0' 'pytest>=8.2.0,<10.0.0'
evaluation-scenarios/.venv/bin/python evaluation-scenarios/scripts/collect_baseline_evidence.py \
  --profile cloudsentinel-eval --region ap-south-2 \
  --output evaluation-scenarios/evidence/baseline-evaluation.json
```

The evaluator reports configuration evidence only. In particular, a world-source security-group rule is not a candidate attack path unless the required route, subnet, and attached-workload evidence is present.
