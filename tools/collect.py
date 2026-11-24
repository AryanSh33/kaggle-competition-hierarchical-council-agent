"""Fan-in for one parallel wave.

    python tools/collect.py work/<wave>    print a table; exit 1 unless every task has a valid result with status ok
    python tools/collect.py --selftest
"""
import json
import pathlib
import sys
import tempfile

STATUS = {"ok", "failed", "blocked"}


def collect(wave):
    wave = pathlib.Path(wave)
    rows = []
    for spec in sorted((wave / "tasks").glob("*.md")):
        i = spec.stem
        try:
            r = json.loads((wave / "results" / i / "result.json").read_text())
            assert r["id"] == i and r["status"] in STATUS, "id/status mismatch"
        except Exception as e:  # missing or malformed: surface it, never skip it
            r = {"id": i, "status": "missing", "summary": f"{type(e).__name__}: {e}"}
        rows.append(r)
    return rows


def show(rows):
    print("| id | status | verdict | seconds | summary | metrics |")
    print("|---|---|---|---|---|---|")
    for r in rows:
        m = " ".join(f"{k}={v}" for k, v in r.get("metrics", {}).items())
        print(f"| {r['id']} | {r['status']} | {r.get('verdict', '')} | {r.get('elapsed_s', '')} | {r.get('summary', '')} | {m} |")


def selftest():
    with tempfile.TemporaryDirectory() as d:
        w = pathlib.Path(d)
        (w / "tasks").mkdir()
        for i in "abcd":
            (w / "tasks" / f"{i}.md").write_text("spec")
        results = {"a": {"id": "a", "status": "ok"}, "b": {"id": "b", "status": "failed"}, "d": {"id": "WRONG", "status": "ok"}}
        for i, res in results.items():
            (w / "results" / i).mkdir(parents=True)
            (w / "results" / i / "result.json").write_text(json.dumps(res))
        got = {r["id"]: r["status"] for r in collect(w)}  # c has no result dir; d's id does not match its task
        assert got == {"a": "ok", "b": "failed", "c": "missing", "d": "missing"}, got
        assert collect(w / "no-such-wave") == []  # an empty wave must not look like success (main exits 1 on it)
    print("selftest ok")


if __name__ == "__main__":
    if sys.argv[1:] == ["--selftest"]:
        selftest()
    elif len(sys.argv) == 2:
        rows = collect(sys.argv[1])
        show(rows)
        sys.exit(0 if rows and all(r["status"] == "ok" for r in rows) else 1)
    else:
        sys.exit(__doc__)
