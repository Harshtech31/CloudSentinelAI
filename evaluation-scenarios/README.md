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
```

This validates catalogue structure only. It does not create AWS resources, call AWS APIs, or assess cloud security.
