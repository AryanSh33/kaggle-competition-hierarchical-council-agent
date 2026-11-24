# Cross-verification protocol

Goal: no number or fact drives a decision until someone other than its author has checked it.

## 1. The claim ledger — `state/claims.md`
Every material statement becomes a claim row:

| ID | Claim | Owner | Evidence (script/output or quote) | Verifier | Status | Notes |
|----|-------|-------|-----------------------------------|----------|--------|-------|
| P-3 | Metric is macro-F1 over 6 classes | Problem Analyst | Evaluation page quote | Validator | VERIFIED | audit/metric_check.py agrees |
| D-7 | 30% of test users unseen in train | Data Analyst | src/eda/overlap.py → 0.302 | Validator | VERIFIED | |
| E-014 | LGBM + lag feats: +0.0041 ± 0.0009 | Evaluator | logs/014.json, oof/014 | Validator | UNVERIFIED | |

ID prefixes: `P` problem, `D` data, `C` council (assumption a proposal relies on), `E` experiment, `V` validator finding.
Statuses: `UNVERIFIED → VERIFIED | REFUTED | HYPOTHESIS` (HYPOTHESIS = cannot be checked yet; may guide experiments, never final decisions).

## 2. Verification matrix — who checks whom

| Produced by ↓ / Checked by → | Problem | Data | Council | Evaluator | Validator |
|---|---|---|---|---|---|
| Problem Analyst (brief, metric) | — | data facts | — | uses metric | **metric, format, rules** |
| Data Analyst (split, CV, leaks) | — | — | Skeptic seat challenges | CV↔LB feedback | **split + CV** |
| Council (proposals) | — | — | Skeptic seat | **runs them** (truth test) | leak review of ideas |
| Evaluator (results) | — | — | — | — | **re-compute from OOF, re-run** |
| Validator (verdicts) | — | — | — | — | Orchestrator spot-checks 1 in 5 |

## 3. Gates
G0 Intake → G1 Problem → G2 Data → G3 Council → G4 Evaluate → G5 Validate → submit → back to G3.
A gate passes only when all claims it depends on are VERIFIED. A REFUTED claim re-opens the earliest gate that relied on it.

## 4. Disagreement resolution
1. State each side as a falsifiable claim.
2. Find the cheapest experiment that separates them (Evaluator runs it on the fixed folds).
3. If none is affordable, choose the option that is more robust to the private test (less tuning, fewer LB-driven choices, simpler model).
4. Record the disagreement, the test, and the outcome in `decisions.md`.

## 5. Signals that force a re-check
- CV↔public-LB Spearman < 0.5 over ≥ 5 submissions, or LB improves while CV worsens → re-open G2.
- A single feature with AUC > 0.9 or a sudden jump > 3× typical gains → Validator leak audit before anything else.
- Fold std > 3× the median across experiments → Data Analyst checks for a bad fold / group leak.
- OOF vs test prediction distribution mismatch → Validator checks train/infer parity.

## 6. Anti-patterns this protocol blocks
Self-grading; tuning on public LB; "improvements" within noise; leakage via fitting outside folds; cherry-picked seeds;
silently changed folds or metric code; final picks by public LB; runtime surprises in code competitions.

## 7. Level-3 workers (parallel waves)
- A worker's `result.json` is **evidence**, not a claim. The lead that dispatched it writes the claim row, cites the result path and owns it;
  the verifier is still a *different* lead (usually the Validator).
- Workers never set a claim status. A worker dispatched by lead X is never evidence in the audit of X's own work: audits use the Validator's workers.
- Decision rules (thresholds, what counts as a pass) are written into the task spec **before** dispatch. Changing them after seeing results voids the probe.
- Missing, failed or blocked tasks are never dropped silently: re-run once, then report INCONCLUSIVE with the reason.
- Extra anti-patterns this blocks: fanning out an untested harness; two workers writing the same file; verdicts invented by workers; parallel arms that secretly depend on each other.
