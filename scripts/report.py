#!/usr/bin/env python3
"""Aggregate stbench eval runs into one table and append it to runs/LOG.md.

Usage:
    python scripts/report.py                      # report every run under runs/
    python scripts/report.py --run health-v1      # only named run dirs (repeatable)
    python scripts/report.py --no-log             # print only, don't touch LOG.md

Reads, per run directory runs/<name>/ (schemas from src/skilltrainbench/evaluate.py):
    eval_result.json      summary rates, per_task scores, usage and cost
    attempts.jsonl        one row per attempt: task_id, task_name, arm, score, passed, status
    learner_ledger.jsonl  per-call token/cost rows tagged with arm -> per-arm tokens/cost
    grader_ledger.jsonl   same, for the grader / simulated user (absent for qf)
"""

from __future__ import annotations

import argparse
import datetime
import json
import sys
from collections import defaultdict
from pathlib import Path

ARM_ORDER = ("baseline", "placebo", "skill")


def read_text_any(path: Path) -> str:
    # the harness writes jsonl without an encoding arg -> cp1252 on Windows
    data = path.read_bytes()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("cp1252", errors="replace")


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    if not path.is_file():
        return rows
    for i, line in enumerate(read_text_any(path).splitlines(), 1):
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(json.loads(line))
        except json.JSONDecodeError:
            print(f"  ! {path.name}:{i}: unparseable line skipped", file=sys.stderr)
    return rows


def ledger_by_arm(path: Path) -> dict[str, dict]:
    """arm -> {tokens, cost} summed over ledger entries (entries without an arm tag land in '-')."""
    out: dict[str, dict] = defaultdict(lambda: {"tokens": 0, "cost": 0.0, "priced": False})
    for e in read_jsonl(path):
        arm = e.get("arm") or "-"
        b = out[arm]
        b["tokens"] += int(e.get("prompt_tokens") or 0) + int(e.get("completion_tokens") or 0)
        if e.get("cost_usd") is not None:
            b["cost"] += float(e["cost_usd"])
            b["priced"] = True
    return out


def cell(value, benchmark: str) -> str:
    if value is None:
        return "-"
    if benchmark == "healthbench":
        return f"{value:.2f}"
    return "PASS" if value >= 0.999 else ("FAIL" if value <= 0.001 else f"{value:g}")


def fmt_tokens(n) -> str:
    return f"{int(n):,}" if n else "-"


def fmt_usd(v) -> str:
    return f"${v:.4f}" if v is not None else "-"


def report_run(run_dir: Path) -> tuple[list[str], list[str]]:
    lines: list[str] = []
    warns: list[str] = []
    result_path = run_dir / "eval_result.json"
    result = {}
    if result_path.is_file():
        try:
            result = json.loads(result_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            warns.append(f"{run_dir.name}/eval_result.json: {e}")
    else:
        warns.append(f"{run_dir.name}: no eval_result.json (run crashed or still going?)")

    attempts = read_jsonl(run_dir / "attempts.jsonl")
    summary = result.get("summary") or {}
    benchmark = result.get("benchmark") or ""
    arms = result.get("arms") or sorted({a.get("arm") for a in attempts if a.get("arm")},
                                        key=lambda a: ARM_ORDER.index(a) if a in ARM_ORDER else 99)

    learner_arm = ledger_by_arm(run_dir / "learner_ledger.jsonl")
    grader_arm = ledger_by_arm(run_dir / "grader_ledger.jsonl")

    # header
    lines.append(f"### {run_dir.name}")
    lines.append("")
    model = (result.get("learner") or {}).get("model", "?")
    bits = [f"domain **{result.get('domain', '?')}** ({benchmark or '?'})", f"learner `{model}`",
            f"n_tasks {summary.get('n_tasks', len({a.get('task_id') for a in attempts}))}"]
    if summary.get("net_delta") is not None:
        bits.append(f"**net_delta {summary['net_delta']:+.4f}**")
    if summary.get("ci95"):
        bits.append(f"ci95 {summary['ci95']}")
    if summary.get("note"):
        bits.append(f"note: {summary['note']}")
    if summary.get("n_invalidated_tasks"):
        bits.append(f"invalidated tasks: {summary['n_invalidated_tasks']}")
    lines.append(" · ".join(bits))
    lines.append("")

    # per-arm table
    passes = defaultdict(lambda: [0, 0])  # arm -> [passed, graded]
    for a in attempts:
        if a.get("passed") is not None:
            p = passes[a.get("arm")]
            p[0] += int(bool(a["passed"]))
            p[1] += 1
    lines.append("| version | arm | rate | passes | learner tokens | learner cost | grader tokens | grader cost |")
    lines.append("|---|---|---|---|---|---|---|---|")
    for arm in arms:
        rate = summary.get(f"{arm}_rate")
        rate_txt = f"{rate:.4f}" if rate is not None else "-"
        p = passes.get(arm)
        pass_txt = f"{p[0]}/{p[1]}" if p else "-"
        la, ga = learner_arm.get(arm), grader_arm.get(arm)
        lines.append(f"| {run_dir.name} | {arm} | {rate_txt} | {pass_txt} "
                     f"| {fmt_tokens(la['tokens']) if la else '-'} | {fmt_usd(la['cost']) if la and la['priced'] else '-'} "
                     f"| {fmt_tokens(ga['tokens']) if ga else '-'} | {fmt_usd(ga['cost']) if ga and ga['priced'] else '-'} |")
    # totals from eval_result (authoritative)
    lu, lc = result.get("learner_usage") or {}, result.get("learner_cost") or {}
    gu, gc = result.get("grader_usage") or {}, result.get("grader_cost") or {}
    lines.append(f"| {run_dir.name} | **total** | | "
                 f"| {fmt_tokens(lu.get('total_tokens'))} | {fmt_usd(lc.get('estimated_usd'))} "
                 f"| {fmt_tokens(gu.get('total_tokens'))} | {fmt_usd(gc.get('estimated_usd'))} |")
    lines.append("")

    # per-task table: prefer eval_result per_task (has task_name), fall back to attempts
    per_task = result.get("per_task") or []
    if per_task:
        lines.append("| task | " + " | ".join(arms) + " |")
        lines.append("|---" * (len(arms) + 1) + "|")
        for row in sorted(per_task, key=lambda r: r.get("task_name") or r.get("task_id", "")):
            name = row.get("task_name") or row.get("task_id", "?")
            cells = [cell(row.get(a), benchmark) for a in arms]
            lines.append(f"| {name} | " + " | ".join(cells) + " |")
        lines.append("")
    elif attempts:
        by_task: dict[str, dict] = defaultdict(dict)
        names: dict[str, str] = {}
        for a in attempts:
            tid = a.get("task_id", "?")
            by_task[tid][a.get("arm")] = a.get("score")
            names[tid] = a.get("task_name") or tid
        lines.append("| task | " + " | ".join(arms) + " |")
        lines.append("|---" * (len(arms) + 1) + "|")
        for tid in sorted(by_task, key=lambda t: names[t]):
            cells = [cell(by_task[tid].get(a), benchmark) for a in arms]
            lines.append(f"| {names[tid]} | " + " | ".join(cells) + " |")
        lines.append("")

    # failed / non-ok attempts, so the failure-reading pass knows where to look
    bad = [a for a in attempts if a.get("passed") is False or (a.get("status") and a["status"] != "ok")]
    if bad:
        lines.append("Failed or non-ok attempts (read these trajectories):")
        for a in sorted(bad, key=lambda r: (r.get("arm", ""), r.get("task_name") or r.get("task_id", ""))):
            score = a.get("score")
            score_txt = f"{score:.2f}" if isinstance(score, float) and benchmark == "healthbench" else score
            lines.append(f"- `{a.get('arm')}` · {a.get('task_name') or a.get('task_id')} · score {score_txt} "
                         f"· status {a.get('status')} · {a.get('trial_dir') or ''}")
        lines.append("")

    # second-reader diagnosis (scripts/second_reader.py), shown before any rule is proposed
    diagnosis = run_dir / "diagnosis.md"
    if diagnosis.is_file():
        body = [ln for ln in diagnosis.read_text(encoding="utf-8").splitlines()
                if not ln.startswith("# ")]
        lines.append(f"#### Second-reader diagnosis ({run_dir.name})")
        lines.extend(body)
        lines.append("")
    return lines, warns


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--runs-dir", default=None, help="runs directory (default: <repo>/runs)")
    ap.add_argument("--run", action="append", default=[], help="only these run dir names (repeatable)")
    ap.add_argument("--no-log", action="store_true", help="print only; do not append to runs/LOG.md")
    args = ap.parse_args()

    repo = Path(__file__).resolve().parent.parent
    runs_dir = Path(args.runs_dir) if args.runs_dir else repo / "runs"
    if not runs_dir.is_dir():
        sys.exit(f"runs dir not found: {runs_dir}")

    skip = {"placebo_skill", "harbor-jobs"}
    run_dirs = [d for d in sorted(runs_dir.iterdir())
                if d.is_dir() and d.name not in skip and (not args.run or d.name in args.run)]
    if not run_dirs:
        sys.exit(f"no run directories matched under {runs_dir}")

    stamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    out = [f"## report {stamp}", ""]
    warns: list[str] = []
    for d in run_dirs:
        lines, w = report_run(d)
        out.extend(lines)
        warns.extend(w)

    text = "\n".join(out)
    print(text)
    for w in warns:
        print(f"WARNING: {w}", file=sys.stderr)

    if not args.no_log:
        log = runs_dir / "LOG.md"
        with open(log, "a", encoding="utf-8") as f:
            f.write(text + "\n")
        print(f"\nappended to {log}", file=sys.stderr)


if __name__ == "__main__":
    main()
