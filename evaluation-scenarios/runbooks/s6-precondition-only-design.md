# S6: Private SSRF-to-IAM Precondition-Only Design

## Status

**Approved design only. No S6 infrastructure, service, workload, request, or IAM permission is deployed by this document.**

## Objective

Evaluate whether CloudSentinel can reject a hypothetical SSRF-to-IAM credential-access candidate path when its required service, network, metadata, and identity preconditions are absent. The outcome is a configuration/graph decision, not an exploit attempt.

## Explicitly prohibited

- A public IP, Internet Gateway, NAT Gateway, public route, public load balancer, or public workload.
- An SSRF-capable endpoint, URL fetcher, proxy, metadata relay, or request to `169.254.169.254`.
- Metadata-token requests, credential retrieval, role assumption, secret-value retrieval, or test credentials.
- Production accounts, applications, data, identities, or network paths.
- Any claim of exploitability, credential access, or a candidate path without all documented preconditions.

## Evaluation model

The local-only model represents the following hypothetical graph nodes:

```text
request input -> instrumented service -> instance metadata service -> IAM role credentials -> test target
```

Each edge is marked **blocked** unless independently supported by a sanitised configuration record. The required conditions are:

1. A reachable service entry point within the authorised scope.
2. A documented, instrumented request-processing condition that would permit an SSRF-like transition.
3. Metadata access permitted by the instance metadata configuration.
4. An attached test role and policy evidence supporting the target action.
5. A non-sensitive test target.

The first three conditions are intentionally absent in the approved design. Therefore the only permitted current result is:

```text
candidate_path: false
classification: preconditions_absent
```

## Safe implementation plan

1. Create a deterministic, in-memory fixture and evaluator under `evaluation-scenarios/`; it must not call AWS.
2. Model blocked edges and assert that no entry-to-target path is produced.
3. Add tests for each required precondition and for rejection when any one is absent.
4. Optionally ingest a sanitised configuration snapshot from an already private, non-SSRF-capable test workload only after a separate deployment plan has been reviewed and approved.
5. Keep S6 in design-only status unless a new explicit approval authorises a bounded private instrumentation phase.

## Completion evidence for the design phase

- This design document.
- A local-only precondition evaluator and passing tests.
- Catalogue status that records S6 as design-only/no deployment.
- No AWS resources created or modified.
