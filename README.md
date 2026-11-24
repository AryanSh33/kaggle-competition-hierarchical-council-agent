# Kaggle Competition Hierarchical Council Agent

A cross-verified multi-agent system for Kaggle competitions, built for [Claude Code](https://claude.com/claude-code).
It is a five-agent "council" with a **third level** added: each lead splits its gate's work into independent tasks and hands
them to **parallel workers**, so the slow parts of a competition (data probing, experiment arms, audits) run side by side.

```
L1  ORCHESTRATOR   CLAUDE.md          phases, gates, budget, claim ledger. Never trains models.
     │
L2  5 LEADS        .claude/agents/    problem-analyst · data-analyst · council · evaluator · validator
     │                                each splits its gate into a wave of independent tasks, dispatched in ONE message
L3  2 WORKERS      .claude/agents/    experiment-worker  runs one experiment spec → numbers + OOF files
                                      probe-worker       runs one read-only probe / check / blind proposal → evidence
```

No claim is accepted until a *different* agent has checked it. Workers produce **evidence**, leads write claims,
only the Validator signs PASS/FAIL, and nobody validates their own work.

## What runs in parallel

| Gate | Lead | Wave | Worker | One task each |
|---|---|---|---|---|
| G2 | Data Analyst | probes | `probe-worker` | split-overlap permutation test · adversarial validation + null · missing/duplicates · leak hunt · baseline noise |
| G3 | Council | seats, then Skeptic attacks | `probe-worker` | one blind seat proposal (blind by construction) · one attack per proposal |
| G4 | Evaluator | arms | `experiment-worker` | one independent experiment arm (or seed shard) |
| G5 | Validator | audits | `probe-worker` | leakage canary · clean re-run · independent metric/Δ recompute · submission-file check · rules check |

The Problem Analyst (G1) is short and stays serial. Gates stay in order; parallelism is *inside* a gate.

## How a wave works
1. The lead does the **serial critical path** itself: harness, pilot run, freezing inputs (sha256 in the specs).
2. It writes one spec per task into `work/<wave>/tasks/` (`templates/task_spec.md`). Decision rules are written **before** anything runs.
3. It dispatches the whole wave in **one message** (at most `max_parallel` tasks). Each worker writes only to its own `work/<wave>/results/<id>/`.
4. Fan-in: `python tools/collect.py work/<wave>` prints one table and exits 1 if any task is missing, failed or blocked.
5. The lead interprets, writes `state/` and the claims. Only the Validator signs a gate.

If a runtime does not let a lead spawn workers, **relay mode** keeps the same hierarchy: the lead ends with
`DISPATCH wave=… tasks=…`, the orchestrator launches the workers and resumes the lead. Details: `protocols/parallel_dispatch.md`.

## Quick start
```bash
git clone https://github.com/<you>/kaggle-competition-hierarchical-council-agent comp-<slug>
cd comp-<slug>
# put the Kaggle files in data/raw/, paste Overview / Evaluation / Data / Rules into state/competition_pages.md, then:
claude
> Start G0 for this competition.
```
The orchestrator creates `state/`, `work/`, `src/` and so on, and copies `templates/` into `state/` itself (kick-off step 1).
To add the council to an existing project, copy `CLAUDE.md`, `.claude/agents/`, `protocols/`, `templates/` and `tools/collect.py`.

## Honest limits
- **Verified:** in the Claude Code desktop app, a level-2 agent spawned two level-3 agents in a single message and they ran concurrently
  (two 20-second jobs started 2 s apart and overlapped for about 18 s). Not verified: speed-up on a full competition. It is bounded by CPU cores
  and by the serial path (harness, merging, ranking), so expect a gain on the experiment and audit phases, not a linear one.
- **Cores:** `max_parallel` defaults to min(4, cores − 1) and workers run single-threaded, so N workers use N cores.
- **Overhead:** a worker launch costs tens of seconds, so jobs under about a minute are batched into one task.
- **Permissions:** every worker runs Bash, and in testing each spawned worker stopped at its own approval prompt. Rather than allowing all of Bash,
  allow your project interpreter narrowly in your own Claude Code settings (for example `Bash(.venv/Scripts/python *)`).
- **Competition Rules:** `.gitignore` keeps `data/`, `oof/`, `preds/`, `subs/`, `work/` out of git. Kaggle rules forbid redistributing competition data
  and often restrict where competition code may be shared; read them before pushing a competition project anywhere public.

## Layout
```
├── CLAUDE.md                      orchestrator (level 1)
├── .claude/agents/                leads (level 2) + workers (level 3)
│   ├── problem-analyst.md  data-analyst.md  council.md  evaluator.md  validator.md
│   └── experiment-worker.md  probe-worker.md
├── protocols/
│   ├── cross_verification.md      claim ledger, verification matrix, gates, level-3 rules
│   ├── parallel_dispatch.md       waves, specs, result.json, native/relay dispatch, fan-in
│   └── metric_playbook.md         metric → loss, post-processing, ensembling, traps
├── templates/                     brief, data_card, proposals, decisions, experiments, claims, validation_report, task_spec
└── tools/collect.py               fan-in for a wave (python tools/collect.py --selftest)
```
Created per competition at kick-off: `state/` (claims, reports), `work/` (waves), `data/raw/`, `src/`, `oof/`, `preds/`, `subs/`, `logs/`.

## Non-negotiables
1. **Trust CV, not the public LB** — unless the Evaluator has shown they correlate.
2. **The CV split must imitate the train→test split.** The Data Analyst infers it; the Validator confirms it.
3. **Every number cites its evidence** (script + output). "Should improve" is not evidence.
4. **An improvement counts only if it beats the noise floor** (fold/seed std), not just the previous score.
5. **Nobody validates their own work.** The Validator never writes the model code it checks.
6. **No submission without a Validator PASS.** Final picks: best robust CV + a diverse hedge.
7. **Decision rules are fixed before a wave is dispatched.** Workers report numbers under those rules, never new rules.
8. **One writer per file.** Parallel tasks share inputs read-only and write to one directory each; dependent work never shares a wave.
9. **Workers never sign off, rank or pick.** Evidence flows up; decisions stay with the leads and the orchestrator.
