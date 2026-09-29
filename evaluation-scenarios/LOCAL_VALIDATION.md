# Local Fixture Validation Report

## Scope

This report records deterministic, in-memory validation of the scenario catalogue and backend attack-graph integration. It is **not** an AWS experiment, benchmark, detection-accuracy result, or cloud-security finding.

- Execution type: `local_in_memory_fixture_validation`
- AWS access: `false`
- Scenario catalogue: S1--S6
- Automated tests: 3 passed

## Results

| Scenario | Expected finding contract | Candidate-path contract | Status |
| --- | --- | --- | --- |
| S1 | `storage_public_access` | No candidate path required | Pass |
| S2 | `overly_permissive_test_iam_policy` | One two-node fixture path | Pass |
| S3 | `laboratory_security_group_exposure` | One two-node fixture path | Pass |
| S4 | `cloudtrail_disabled_in_test_account` | No candidate path required | Pass |
| S5 | Three multi-stage fixture conditions | One four-node fixture path | Pass |
| S6 | Instrumented service and test identity conditions | One three-node fixture path | Pass |

## Interpretation

The runner confirms that the versioned scenario and ground-truth catalogues can drive deterministic in-memory fixtures through the repository's `AttackGraph`, `AttackPathFinder`, and `AttackPathScorer` classes. It provides regression coverage for scenario handling before live AWS work begins.

The output does **not** demonstrate that CloudSentinel detects real AWS configurations, that its candidate paths are exploitable, or that its local fixture scores represent calibrated risk. Those claims require controlled AWS deployment, independent path review, baseline comparisons, and archived execution evidence.

## Reproduction

From the repository root:

```bash
python3 evaluation-scenarios/scripts/validate_catalog.py
python3 evaluation-scenarios/scripts/run_local_scenarios.py
backend/.venv/bin/python -m pytest evaluation-scenarios/tests
```
