# Parallel dispatch protocol (level 2 → level 3)

Parallelism lives **inside** a gate. A lead splits the gate's independent work into a *wave* of tasks, dispatches the whole
wave at once, then fans the results back in. Gates themselves stay in order.

## 1. Wave layout
```
work/<wave>/                  wave id: w<NN>-<lead>-<topic>, e.g. w04-evaluator-arms
  tasks/<id>.md               one spec per task, written by the lead (templates/task_spec.md)
  results/<id>/               the worker's ONLY write location: result.json, log.txt, probe.py, oof files, ...
```
`<id>` matches `[A-Za-z0-9_.-]+` and is unique in the project (experiment IDs are immutable).

## 2. result.json
```json
{"id": "E-004a", "status": "ok", "verdict": "CONFIRMED", "summary": "one line",
 "metrics": {"cv_mean": 0.8334}, "files": ["oof.csv"], "elapsed_s": 41.2}
```
`status` is execution state: `ok` | `failed` | `blocked`. `verdict` (probes only) is the answer under the spec's decision rule.
A `FAIL` or `REFUTED` verdict with status `ok` is a finding, not an error.

## 3. Dispatch
- **Native (default).** The lead has the Agent tool. It calls it once per task **in a single message**:
  `subagent_type: experiment-worker | probe-worker`, prompt `Run task work/<wave>/tasks/<id>.md`.
  At most `max_parallel` per message; the next batch goes out when the first one finishes.
- **Relay (fallback if a lead cannot spawn).** The lead writes the specs and ends its reply with
  `DISPATCH wave=<id> worker=<type> tasks=<id,id,...>`. The orchestrator makes the same calls (one message, batches of `max_parallel`)
  and, when all have finished, resumes the lead with `WAVE_DONE <id>`. The lead still owns the plan, the fan-in and the claims.

## 4. Rules that make parallel runs safe
- **One writer per file.** Each worker writes only under its own `results/<id>/`. Code, folds, data and `state/` are read-only for the
  whole wave; the lead freezes them first and puts a sha256 in the spec.
- **No hidden dependencies.** If task B needs A's output, B goes in the next wave.
- **Decision rules before dispatch.** Thresholds and pass/fail conditions are in the spec. Changing them after seeing results voids the probe.
- **Cores.** `max_parallel` = min(4, CPU cores − 1) unless the user sets it. Workers run single-threaded (`OMP_NUM_THREADS=1`, `n_jobs=1`),
  so N workers use N cores. Oversubscribing makes every task slower.
- **Overhead.** A worker launch costs tens of seconds. Do not dispatch jobs shorter than about a minute; batch them into one task.
- **Serial critical path stays with the lead:** harness, pilot run, freezing inputs, merging, ranking, claims, verdicts.
- **Independence.** A worker dispatched by lead X is never audit evidence for X's own work. Audits use the Validator's workers.

## 5. Fan-in
`python tools/collect.py work/<wave>` prints one table and exits 1 if any task is missing, malformed, failed or blocked.
The lead re-runs failed tasks once; a second failure is reported as INCONCLUSIVE with the reason, never dropped.
The lead then computes comparisons, writes `state/` files and claims, and cites `work/<wave>/results/<id>/result.json` as evidence.
