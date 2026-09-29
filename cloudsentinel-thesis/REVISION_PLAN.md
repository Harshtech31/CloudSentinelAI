# CloudSentinel AI Thesis Revision Plan

## Goal

Prepare a defensible, internally consistent IEEE research paper by first resolving research-status, evidence, and methodology issues, then completing controlled evaluation and IEEE-compliant presentation. The original thesis source remains available as supporting material; the submission source is maintained separately in `ieee-paper/paper.tex`.

## Guiding decision — complete before all other work

### Decide the thesis type

Choose **one** of the following paths with the supervisor:

- **Proposal/design thesis (recommended unless reproducible evidence already exists):** the framework and evaluation are planned but not yet fully implemented or executed.
- **Implementation/evaluation thesis:** use this only when the implementation, raw outputs, controlled measurements, environment configuration, and analysis are available for review and reproduction.

The existing wording in Chapters 7, 10, and 11 mainly supports the proposal/design path. This decision controls the wording, evidence requirements, Chapters 7–12, and the appendix.

### Acceptance criteria

- Every chapter uses the same tense and status.
- Claims about deployment, experiments, validation, performance, and results agree with the repository evidence.
- No numerical results are presented without disclosed data or a stated simulation method.
- Chapter 12 does not use words such as “demonstrates,” “shows,” or “validates” unless the corresponding completed evidence is included.

---

## Phase 1 — Correct research-status and unsupported-result claims

### Files

- `chapters/chapter7_research_methodology.tex`
- `chapters/chapter9_implementation_and_technology_stack.tex`
- `chapters/chapter10_experimental_design_and_evaluation_plan.tex`
- `chapters/chapter11_expected_results_and_discussion.tex`
- `chapters/chapter12_conclusion_and_future_scope.tex`
- `appendix/appendix_a.tex`

### Actions

1. **If this is a proposal/design thesis**
   - Use prospective wording consistently: “will implement,” “is proposed,” “will be evaluated.”
   - Rename Chapter 11 to clarify that it contains expected outcomes, hypotheses, or acceptance criteria.
   - Remove or clearly label risk scores, response-time values, scalability figures, and alert-reduction percentages as illustrative targets rather than observed findings.
   - Rewrite the conclusion to describe the framework as proposed, not validated.
   - Remove statements that the AWS environment was deployed or attack paths were generated unless that work actually occurred.

2. **If this is an implementation/evaluation thesis**
   - Replace scaffold/stub components with the actual implemented behaviour, or narrow the claimed implementation scope.
   - Record the exact source version, cloud region, services, machine specifications, library/tool versions, AWS account setup, and experiment dates.
   - Preserve raw output and measurement data in a reproducible location.
   - Replace expected values with measured values and disclose repetitions, aggregation method, variance, and failures.

3. Remove unresolved placeholders such as “or the region you used” and “or your instance type.”
4. Align the objectives and experiment catalogue.
   - Chapter 1 promises validation of an “SSRF to IAM credential theft” path, while Chapter 10’s current five scenarios do not test SSRF.
   - Either add a safe, isolated, controlled scenario with explicit ground truth and no external exposure, or remove/narrow the Chapter 1 claim.
5. In Chapter 12, replace outcome language with design/proposal language if the proposal path is selected.

### Acceptance criteria

- No passage implies that unperformed work was completed.
- Every reported number has a traceable source, measurement method, and experimental context.
- The conclusion does not claim validation beyond the available evidence.

---

## Phase 2 — Create the IEEE paper submission source

### Files

- `ieee-paper/paper.tex`
- `references.bib`
- `IEEEtran.bst`

### Actions

1. Use the generic two-column `IEEEtran` conference class unless the target venue provides a different official template.
2. Maintain the IEEE paper separately from the long-form thesis source so supporting material is not lost.
3. Use IEEE paper structure: title and author block, abstract, keywords, introduction, related work, proposed framework, evaluation design, discussion/limitations, conclusion, and references.
4. Do not include thesis-only front matter, a table of contents, List of Figures, List of Tables, or chapter-based organisation in the IEEE submission.
5. Keep all proposal/evaluation claims evidence-safe until Phase 8 produces reproducible results.

### Acceptance criteria

- `ieee-paper/paper.tex` compiles with `IEEEtran` using a two-column layout.
- The paper has a valid abstract, IEEE keywords, numbered sections, figures/tables with captions, and IEEE-style references.
- The original thesis source remains untouched apart from evidence-correction work already completed.

---

## Phase 3 — Repair the literature base and citations

### Files

- `references.bib`
- `chapters/chapter1_introduction.tex`
- `chapters/chapter2_background_study.tex`
- `chapters/chapter3_state_of_the_art_and_existing_cloud_security_solutions.tex`
- `chapters/chapter4_literature_review_and_critical_analysis.tex`
- `chapters/chapter5_research_gap_analysis.tex`
- `chapters/chapter8_system_design_and_algorithmic_framework.tex`
- `chapters/chapter9_implementation_and_technology_stack.tex`
- `chapters/chapter10_experimental_design_and_evaluation_plan.tex`
- `chapters/chapter11_expected_results_and_discussion.tex`
- `appendix/appendix_a.tex`

### Actions

1. Verify every bibliography record against a publisher page, DOI resolver, conference proceedings, or official documentation.
   - Prioritise the `homoliak2019cloud` entry, whose current title/DOI metadata needs verification.
2. Add citations to the three detailed studies in Chapter 4 (currently described as “Paper 1–3”).
3. Cite the NIST cloud-computing definition immediately after the quoted/paraphrased definition in Chapter 2.
4. Add evidence for broad factual claims about misconfigurations, cloud incidents, breach causes, alert volume, and cloud adoption.
5. Cite primary documentation for AWS Security Hub, AWS Config, Prowler, ScoutSuite, Wiz, Prisma Cloud, and Microsoft Defender for Cloud. Include product/version/date scope where appropriate.
6. Cite the specific versions of CIS Benchmarks, NIST guidance, graph/attack-graph literature, and LLM/XAI evaluation literature used in the design.
7. For each comparison-table cell, specify whether it is based on vendor documentation, academic literature, or measured evaluation results.

### Acceptance criteria

- Every non-obvious factual, technical, comparative, or statistical claim has an appropriate source.
- All bibliography entries are real, complete, and match their cited claims.
- Product-capability claims are time/version scoped and do not use unsupported absolutes such as “none” or “full.”

---

## Phase 4 — Define a precise research contribution and scope

### Files

- `chapters/chapter1_introduction.tex`
- `chapters/chapter3_state_of_the_art_and_existing_cloud_security_solutions.tex`
- `chapters/chapter4_literature_review_and_critical_analysis.tex`
- `chapters/chapter5_research_gap_analysis.tex`
- `chapters/chapter6_proposed_framework_and_system_architecture.tex`

### Actions

1. Replace the broad claim that graph/context/AI integration is absent from existing tools with a narrow, verifiable research gap.
2. State the contribution in one to three measurable claims, for example:
   - a defined AWS asset/relationship schema;
   - a specific, evidence-backed attack-path validity model;
   - a transparent risk-prioritisation heuristic;
   - a grounded LLM explanation approach with human review.
3. Establish a controlled vocabulary and use it throughout:
   - “LLM-assisted explanation” for generated prose;
   - reserve “explainable AI/XAI” only if an actual explainability method is implemented and evaluated;
   - distinguish “candidate attack path” from a technically validated exploitation chain;
   - distinguish implemented components from future work.
4. Keep the scope AWS-specific unless multi-cloud support is actually part of the implementation and evaluation.
5. Remove “automated remediation scripts” from objectives unless remediation code is generated safely, validated, and gated by human approval. Otherwise state “remediation recommendations.”
6. Add a compact **claim-to-evidence matrix** in the appendix. For every contribution claim, map it to its design/implementation artifact, evaluation question, metric, evidence source, and stated limitation.

### Acceptance criteria

- The novelty claim is not contradicted by the product and literature review.
- The problem statement, objectives, scope, architecture, evaluation, and conclusion use the same terminology.
- Each claimed contribution maps to an implementation/design element and an evaluation measure.
- The claim-to-evidence matrix makes the scope and limitations of every contribution auditable.

---

## Phase 5 — Make the framework and methodology reproducible

### Files

- `chapters/chapter6_proposed_framework_and_system_architecture.tex`
- `chapters/chapter7_research_methodology.tex`
- `chapters/chapter8_system_design_and_algorithmic_framework.tex`
- `chapters/chapter10_experimental_design_and_evaluation_plan.tex`
- `appendix/appendix_a.tex`

### Actions

1. Specify the system data model.
   - Define node types, edge types, attributes, evidence sources, asset identity rules, and data refresh semantics.
   - Clearly distinguish the knowledge graph from the derived attack graph.
2. Specify a threat model.
   - Define attacker starting conditions, required privileges, exploit preconditions, trust boundaries, and what a graph edge can and cannot prove.
3. Define path analysis.
   - State whether the system calculates reachability, shortest paths, bounded top-*k* paths, or all simple paths.
   - Add actual pseudocode, input/output definitions, stopping/pruning rules, and defensible best/worst-case complexity.
4. Define risk scoring.
   - Give all variable ranges, data sources, weights, thresholds, normalisation method, and reason for each factor.
   - Avoid double-counting exposure in both asset criticality and the final risk score unless justified.
   - Treat the score as a heuristic until calibrated and validated; add sensitivity analysis for weights.
5. Define LLM safety and evidence grounding.
   - Restrict the LLM input to approved metadata.
   - Require that explanations reference deterministic findings and known evidence.
   - State that recommendations require human review and must not be executed automatically.
6. Define AWS experiment safety and cost controls.
   - Use isolated, non-production test account(s), least-privilege experiment roles, and no real sensitive data.
   - Tag all experimental resources; define cleanup ownership, cleanup deadlines, and verification.
   - Configure budget alarms and service quotas where appropriate.
   - Do not intentionally expose services beyond the controlled lab environment; document containment boundaries and emergency teardown steps.

### Acceptance criteria

- Another researcher can reconstruct the framework from the text and appendix.
- Risk and path outputs are operationally defined rather than described only at a high level.
- The thesis does not claim a candidate graph path is an automatically proven exploit path.

---

## Phase 6 — Build a valid evaluation protocol

### Files

- `chapters/chapter7_research_methodology.tex`
- `chapters/chapter10_experimental_design_and_evaluation_plan.tex`
- `chapters/chapter11_expected_results_and_discussion.tex`
- `appendix/appendix_a.tex`

### Actions

1. Define scenarios and ground truth.
   - Use a fixed scenario catalogue with configuration, expected findings, expected/forbidden paths, and severity labels.
   - Include negative controls as well as intentionally vulnerable scenarios.
   - Have ground truth independently reviewed where possible.
2. Define the unit of evaluation and metrics before experiments.
   - State separately whether precision, recall, and F1 apply to findings, assets, graph edges, complete paths, or ranked recommendations.
   - Define TP, FP, TN, FN, the path-level match rule, and treatment of partial matches.
   - Define the denominator for “alert reduction,” what counts as one consolidated alert, and the reference baseline alert set.
   - Define “accuracy of prioritisation,” including the reference ranking, severity labels, and aggregation rule.
   - Separate finding detection from path prioritisation, explanation quality, and remediation usefulness.
3. Make baseline comparison fair and distinguish comparison types.
   - Record each baseline’s version, account/region, enabled standards, scan scope, credentials, configuration, and execution date.
   - Define how alerts/findings from different tools are normalised before comparison.
   - Label “None/Partial/Full” capability tables as documentation-based feature comparisons, include their source/version/access date, and do not present them as measured performance results.
4. Make measurements reproducible.
   - Record hardware, cloud configuration, repetitions, timing boundaries, API retries/failures, average/median, and variance.
5. If usability or explanation quality is evaluated:
   - Define participants or expert raters, task scripts, scoring rubric, sample size, and inter-rater agreement.
   - Obtain any required institutional ethics approval before collecting human-participant data.

### Acceptance criteria

- Each evaluation question has a ground-truth source and metric.
- Reported results can be recreated from documented configuration and raw data.
- Claims of superiority are scoped to the specified scenarios and baseline configurations.

---

## Phase 7 — Repair LaTeX hierarchy, tables, figures, blank pages, and appendix organisation

### Files

- `main.tex`
- all files in `chapters/`
- `appendix/appendix_a.tex`

### Actions

1. Replace manual chapter headings with `\chapter{...}` because the document uses the `report` class.
2. Remove manually typed chapter/section numbers from headings; let LaTeX number them automatically.
3. Use `\section`, `\subsection`, and `\subsubsection` only for subordinate headings.
4. Convert tables to proper table structures.
   - Use `\caption{...}` and `\label{...}` inside each `table` or `longtable`.
   - Replace manual labels such as “Table 11.3” in body text with `\ref{...}`.
   - Give appendix tables appendix-specific labels and titles.
5. Correct figures.
   - Use a single sizing constraint such as `width=\textwidth` and preserve aspect ratio.
   - Avoid `[H]` unless placement is essential.
   - Place each figure near its first discussion and cite it with `\ref{...}`.
   - Replace generic appendix captions with descriptive captions explaining what the reader should learn from each figure.
6. Remove manual `\\` line breaks in normal prose and list text where not semantically required.
7. Remove blank and nearly empty pages.
   - Inspect the current blank PDF pages (45, 62, 68, 79, 88, and 134) after each clean build.
   - Remove or relocate unused “Additional Figures” sections and avoid forced float placement that leaves empty pages.
   - Confirm that the List of Tables contains properly captioned tables; remove it only if university rules permit and no tables remain.
   - Remove duplicated content such as repeated Table 11.6 material.
8. Reduce the appendix to supporting material:
   - scenario setup and configuration;
   - full rule catalogue;
   - detailed pseudocode;
   - prompt templates and evidence schema;
   - raw results and measurement logs;
   - baseline configurations;
   - questionnaires/rubrics.
   Move duplicated architecture, literature, and contribution narrative back to the main body or remove it.

### Acceptance criteria

- The table of contents shows `Chapter 1`, `Chapter 2`, etc., not `0.1` numbering.
- The List of Tables and List of Figures include all items with meaningful captions; neither is unexpectedly empty.
- The final PDF has no unexplained blank or nearly empty pages.
- No placeholders remain, and there are no material overfull boxes in the final PDF.

---

## Phase 8 — Build and validate the controlled AWS scenario catalogue

This phase upgrades the work from a design/proposal thesis to an implementation/evaluation thesis **only after** the listed scenarios are implemented, executed, and documented with reproducible evidence. The versioned source of truth is the root-level `evaluation-scenarios/` directory: `catalog.json` defines the scenario boundaries, `ground-truth/catalog.json` records the expected labels and path conditions, and `scripts/validate_catalog.py` validates catalogue structure without accessing AWS.

### Prerequisites

- A dedicated, authorised, non-production AWS account (or equivalent isolated accounts).
- Least-privilege experiment roles; no real sensitive data, customer data, or production credentials.
- Resource tags identifying the project, owner, scenario, and cleanup date.
- Budget alarms, service quotas, documented emergency teardown, and a verified cleanup checklist.
- A version-pinned CloudSentinel build and version-pinned baseline tools.
- A ground-truth catalogue reviewed before each test run.

### Controlled scenario catalogue

1. **Public S3 storage exposure**
   - Configure a test-only S3 bucket with the approved, deliberately weak access policy.
   - Ground truth: expected storage finding, affected resource, severity rationale, and permitted remediation recommendation.
   - Evidence: configuration snapshot, CloudSentinel output, baseline outputs, normalized finding comparison, cleanup confirmation.

2. **Overly permissive IAM policy**
   - Assign an intentionally over-broad policy to a dedicated test principal only.
   - Ground truth: expected identity finding, relevant permissions, and candidate privilege-escalation relationship if supported by evidence.
   - Evidence: policy document, collector output, graph edges, finding comparison, and cleanup confirmation.

3. **Insecure network configuration**
   - Model the required security-group exposure only inside the isolated lab; do not expose an intentionally weak service to the public Internet.
   - Ground truth: expected network finding, affected endpoint, permitted entry-point classification, and required candidate-path preconditions.
   - Evidence: security-group configuration, reachability model, scan outputs, and cleanup confirmation.

4. **Disabled CloudTrail logging**
   - Disable or simulate the required audit-logging condition only in the dedicated test account and record the time window.
   - Ground truth: expected logging finding and prescribed remediation.
   - Evidence: CloudTrail configuration before/after, scan outputs, and restoration confirmation.

5. **Multi-stage candidate path**
   - Combine only test resources: an EC2 workload, bounded test network configuration, a test IAM role, test-only Secrets Manager access, and a non-sensitive S3 bucket.
   - Ground truth: the expected candidate path, evidence per edge, attacker assumptions, forbidden paths, and the reviewer’s path-validity decision.
   - Evidence: graph export, rule findings, path output, edge-evidence record, baseline outputs, and teardown record.

6. **SSRF-to-IAM credential-access candidate path**
   - Use a deliberately instrumented non-production test service to model application-to-metadata access in the isolated account. Do not use production credentials, real sensitive data, or public exposure.
   - Ground truth: configuration and identity preconditions required for the candidate path, plus the conditions that invalidate it.
   - Evidence: approved scenario design, configuration snapshot, graph/path output, independent reviewer assessment, and cleanup confirmation.

### Required evidence and measurements

For every scenario:

1. Save an immutable configuration snapshot and the ground-truth label set before scanning.
2. Run CloudSentinel and each selected baseline using the same account scope, enabled checks, credentials/permissions, and documented tool version.
3. Preserve raw outputs, normalized findings, graph exports, candidate-path evidence, logs, timings, and error/failure records.
4. Repeat measurements under the documented configuration; report run count, timing boundaries, median/mean, and variability.
5. Evaluate finding-level precision, recall, F1, false positives, and false negatives against the scenario labels.
6. Review each candidate path against its preconditions; report exact matches, partial matches, invalid paths, and reviewer disagreement separately.
7. Treat LLM-generated explanations as advisory. Score them with a defined rubric for evidence consistency, technical accuracy, clarity, and actionable remediation; retain human-review results.
8. Verify and record cleanup of all AWS resources after each run.

### Update the thesis only after evidence exists

- Add a reproducibility appendix containing the scenario catalogue, account-safety protocol, tool versions, configurations, raw-result locations, and cleanup evidence.
- Replace Chapter 11 hypotheses and illustrative tables with measured results, including uncertainty and limitations.
- Update Chapter 10 with the executed environment specification, exact baseline configurations, and the final metric definitions.
- Update Chapter 12 from proposal language to bounded, evidence-backed conclusions. For example, claims must be scoped as “in the controlled scenarios evaluated,” never as universal cloud-security claims.
- Complete the claim-to-evidence matrix by linking each contribution to its implementation artifact, scenario, metric, result, and limitation.

### Acceptance criteria

- All six scenarios have approved ground truth, raw evidence, and verified cleanup records.
- Every performance, detection, prioritisation, alert-reduction, or explanation-quality statement in the thesis is traceable to recorded evidence.
- Candidate attack paths are reviewed against explicit preconditions and are never presented as proven exploitation solely because graph edges exist.
- The supervisor approves the transition from proposal/design wording to implementation/evaluation wording.

---

## Phase 9 — Final verification and supervisor review

### Actions

1. Run a clean LaTeX build and resolve unresolved references/citations.
2. Inspect the PDF page by page for clipped tables, distorted figures, blank pages, heading hierarchy, table/figure references, and bibliography formatting.
3. Check every claim in the abstract, introduction, results, and conclusion against the evidence in the thesis.
4. Ask the supervisor to review:
   - thesis type and claim scope;
   - novelty statement;
   - final evaluation protocol/results;
   - university formatting and front-matter requirements.
5. Keep a final checklist showing that all reviewer comments were addressed.

### Suggested build and validation checks

```bash
cd cloudsentinel-thesis
latexmk -C
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
grep -nEi 'undefined (reference|citation)|LaTeX Warning: There were undefined|Overfull \\hbox|Overfull \\vbox' main.log
```

Then inspect the generated PDF page by page, specifically checking front matter, contents numbering, the List of Tables, the known blank-page locations, all wide tables, figure aspect ratios, citation links, and bibliography formatting. These are actual clean-build and inspection checks; do not substitute PDF metadata for validation.

### Submission readiness checklist

- [ ] Thesis type is consistent across all chapters.
- [ ] All results are measured or explicitly labelled as planned/illustrative.
- [ ] Every central claim is cited or supported by disclosed evidence.
- [ ] Bibliography entries have been verified.
- [ ] Research contribution is specific and measurable.
- [ ] Framework, threat model, and scoring are reproducible.
- [ ] Evaluation has an explicit unit of analysis, ground truth, metrics, baselines, and reproducible setup.
- [ ] AWS testing is isolated, safe, tagged, budget-controlled, and cleaned up.
- [ ] Claim-to-evidence matrix maps each contribution to its evidence and limitation.
- [ ] Required front matter and university formatting requirements are complete.
- [ ] Chapter/table/figure numbering is automatic and correct.
- [ ] Appendix contains supporting evidence rather than duplicated narrative.
- [ ] Final PDF has been visually inspected and approved by the supervisor.
- [ ] If implementation/evaluation claims are used, all six controlled AWS scenarios have been executed with archived evidence and cleanup records.
