# Task <id>
wave: <wave-id>                 lead: <evaluator | data-analyst | council | validator>
worker: <experiment-worker | probe-worker>
objective: <one sentence>
python: <interpreter, e.g. .venv/Scripts/python or .venv/bin/python>
inputs: <files the worker may read>          sha256: <optional hash of folds / data / candidate, frozen by the lead>
output_dir: work/<wave>/results/<id>/        # the ONLY place the worker may write
budget: <minutes>

## experiment-worker
command: <exact command from the project root; must accept --out <output_dir> and write only there>
seeds: <list>
expected_files: <files that must exist under output_dir>

## probe-worker
question: <the falsifiable question>
method: <what to compute, with seeds / permutation counts>      (council seat: persona: <seat text>, blind: true)
decision_rule: <fixed BEFORE dispatch, e.g. "CONFIRMED if abs(z) < 2 over 1000 permutations">
independent: <true | false>        do_not_read: <paths, when independent: true>
