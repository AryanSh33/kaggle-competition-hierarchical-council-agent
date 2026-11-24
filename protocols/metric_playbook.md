# Metric playbook — what each metric implies

Used by the Problem Analyst (implications), Council (strategy) and Evaluator (post-processing). Always confirm
the exact definition on the competition's Evaluation page; hosts often modify standard metrics.

| Metric | Train on | Post-processing (tune on OOF only) | Ensembling | Traps |
|---|---|---|---|---|
| **ROC-AUC** | logloss / binary objective | none needed; monotone transforms don't change it | rank-average | Only ranking matters; per-group AUC averaged ≠ global AUC — check which |
| **Log loss / cross-entropy** | logloss | clip to [ε, 1−ε]; temperature / Platt / isotonic calibration on OOF | average probabilities (or logits); check calibration after blending | Overconfident models get destroyed; class-prior shift between train and test matters |
| **F1 / F-beta (binary)** | logloss | optimise threshold on OOF | average probs, then threshold | Threshold that is best on OOF can drift if test prevalence differs |
| **Macro-F1 (multiclass)** | CE, maybe class weights | per-class thresholds / prior adjustment on OOF | average probs | Rare classes dominate the metric; stratify folds |
| **Accuracy / balanced acc.** | CE | argmax; prior adjustment for balanced | average probs | Calibration irrelevant; class balance matters for balanced |
| **QWK (quadratic weighted kappa)** | regression (MSE) or ordinal | optimise cut-points on OOF (OptimizedRounder-style) | average continuous preds, then cut | Very noisy on small tests → high shake-up risk |
| **RMSE** | MSE | clip to plausible range | weighted mean | Outliers dominate; check if removing train outliers helps CV |
| **RMSLE** | MSE on log1p(y), invert with expm1 | clip ≥ 0 | mean in log space | Training on raw y is a common mistake |
| **MAE** | L1 / Huber / quantile 0.5 | median-type adjustments | median or weighted mean | Mean-optimising models are biased for MAE |
| **MAPE / SMAPE** | custom or log target; sample weights 1/y | shrink predictions slightly (asymmetric penalty) | geometric/median blends | Zeros explode MAPE; SMAPE rewards under-prediction |
| **Pinball / quantile** | quantile objective per quantile | enforce monotone quantiles (sort) | average per quantile | Crossing quantiles |
| **Pearson / Spearman correlation** | MSE or correlation loss | scale irrelevant; ranks for Spearman | rank-average (Spearman) or z-score average | Per-group correlation averaged (finance-style) needs group-wise evaluation |
| **MAP@K / NDCG / recall@K** | ranking (LambdaRank), two-stage retrieve→rerank | dedupe, fill to K with popular items | score/rank fusion (RRF) | Candidate recall caps the score — measure it |
| **Dice / IoU / mAP (vision)** | BCE + Dice / Lovász; detection losses | threshold, min-area filter, morphology, NMS/WBF tuning, TTA | WBF for boxes; mean masks then threshold | Empty-mask images; resolution mismatch at inference |
| **Text generation (BLEU/ROUGE/LLM-judge)** | CE / preference tuning | length control, decoding params tuned on OOF | output selection/reranking | Judge metrics reward style; check length bias |

## General rules
- Tune every post-processing parameter on OOF with the same folds, and report its gain with the paired test.
- If the metric is computed per group and averaged, evaluate CV the same way.
- Probability-averaging, rank-averaging and stacking can rank differently — let OOF decide.
- High-variance metric + small private test → favour robust ensembles and conservative final picks.
