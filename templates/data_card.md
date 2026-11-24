# Data card — <competition name>
Owner: Data Analyst · Last updated: <date> · Gate G2 status: OPEN / PASSED

Format for every finding: **claim → evidence (script + numbers) → implication**, with claim ID `D-n`.

## 1. Inventory
| File | Rows | Cols | Size | Key(s) | Notes |
|---|---|---|---|---|---|

Brief claims checked: P-… VERIFIED / REFUTED

## 2. Target
Distribution / imbalance / outliers / label-noise evidence

## 3. Features
Missingness (train vs test) · cardinality · suspicious columns · correlated clusters

## 4. Structure
- Time: train range … test range … → relation
- Groups/entities: key … overlap train↔test …%
- Duplicates (within train / across train↔test):

## 5. Adversarial validation
AUC (mean ± std over folds): · Top drifting features: · Handling plan per feature:

## 6. Leak hunt
| Feature | Single-feature AUC/corr | Leak? | Allowed by rules? | Action |
|---|---|---|---|---|

## 7. Inferred train→test split
Hypothesis: … Evidence: …

## 8. Recommended CV
Splitter · k · seed · stratify on · group on · gap/embargo · file: `data/folds.csv`
Why it mimics the test split:
Validator check: PASS / FAIL

## 9. Sanity baselines
| Model | Fold scores | Mean ± std |
|---|---|---|
| Constant / prior | | |
| Default GBDT | | |

## 10. Facts the Council must respect
1.
