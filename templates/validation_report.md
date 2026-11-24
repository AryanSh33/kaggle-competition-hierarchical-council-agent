# Validation report
Owner: Validator (independent — did not write the audited code)

## Audit #<n> — <date> — Gate: G1 / G2 / G5 / Final selection
Candidate: <sub file / exp IDs / code hash>

| Area | Check | Result | Evidence | Owner of fix |
|---|---|---|---|---|
| Leakage | transforms fit inside folds | | | |
| Leakage | shuffled-target CV ≈ chance | | | |
| Leakage | no future/test statistics | | | |
| Leakage | single-feature AUC scan | | | |
| Leakage | pseudo-label/teacher fold hygiene | | | |
| Repro | clean re-run matches CV within tol | | | |
| Metric | independent metric = Evaluator CV | | | |
| Metric | Δ and verdict recomputed from OOF | | | |
| Submission | format/ids/rows/dtypes/range/NaN | | | |
| Submission | test-pred vs OOF distribution | | | |
| Rules | runtime ≥20% margin on full hidden test, internet off, external data OK | | | |
| LB overfit | # decisions informed by public LB | | | |

**Verdict:** PASS / PASS-WITH-NOTES / FAIL
Not checked (UNVERIFIED):
Notes:
