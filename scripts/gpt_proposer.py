#!/usr/bin/env python3
"""GPT proposer: one OpenAI call that drafts a complete candidate skill folder.

Curator-side only (lives in scripts/). Modelled on second_reader.py and reuses
its trajectory assembly (skill text stays redacted in trajectories; the current
SKILL.md is passed separately and explicitly, per the round-loop spec).

Usage:
    uv run python scripts/gpt_proposer.py runs/qf-v0 --domain qf --round 1 --proposer gpt-a
    ... [--arm baseline] [--skill submissions/denden/qf] [--model m] [--cap 0.40]

Writes submissions/denden/<domain>-candidates/<round>-<proposer>/SKILL.md (+ any
tool files the model proposes). The orchestrator still runs check-skill and the
eval; proposers never run evals.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from second_reader import (REPO, api, assemble, load_env_key, pick_model,  # noqa: E402
                           price_for, read_jsonl)

TEAM_DIR = "submissions/denden"

BRIEF = (
    "Write a complete SKILL.md that would have prevented the failures shown. "
    "Numbered rules with stable ids, one rule per failure cause, under 40 lines, "
    "no generic advice, no task text or answers. Offline scripts allowed in the "
    "folder if they replace arithmetic, validation or formatting the learner gets wrong."
)

SYSTEM = (
    "You are a skill curator for a frozen coding agent (GLM 5.3 Flash in OpenHands). "
    "A 'skill' is a folder mounted read-only into the agent's task container: SKILL.md "
    "(valid YAML frontmatter with name and description, then numbered rules R1, R2, ...) "
    "plus optional offline helper scripts. The agent reads SKILL.md before working. "
    "Scripts must be stdlib-only Python, runnable offline with no network or credentials.\n\n"
    + BRIEF + "\n\n"
    "Hard constraints: under 40 lines of SKILL.md; rules must be behaviour-specific "
    "(a placebo skill already covers 'be careful, work step by step'); never include "
    "task text, answers, rubric text, external URLs or credentials.\n\n"
    "Return ONLY a JSON object: {\"files\": {\"SKILL.md\": \"<content>\", ...}} where every "
    "key is a relative file path in the skill folder. Include SKILL.md always; add helper "
    "scripts only when they deterministically fix an observed failure."
)


def main() -> None:
    ap = argparse.ArgumentParser(description="GPT proposer for one candidate skill")
    ap.add_argument("run", help="latest eval run folder for the domain")
    ap.add_argument("--domain", required=True)
    ap.add_argument("--round", required=True)
    ap.add_argument("--proposer", required=True, help="candidate label, e.g. gpt-a")
    ap.add_argument("--arm", default="skill", help="arm whose failures to learn from")
    ap.add_argument("--skill", default=None, help="current skill folder (default team folder)")
    ap.add_argument("--model", default=None)
    ap.add_argument("--cap", type=float, default=0.40, help="max USD for this proposal call")
    ap.add_argument("--max-fails", type=int, default=6, help="trajectories to include")
    args = ap.parse_args()

    run_dir = Path(args.run)
    if not run_dir.is_absolute():
        run_dir = REPO / run_dir
    attempts = read_jsonl(run_dir / "attempts.jsonl")
    fails = [a for a in attempts if a.get("arm") == args.arm and a.get("passed") is False]
    if not fails:
        sys.exit(f"gpt_proposer: no failed {args.arm!r} attempts in {run_dir}")
    fails = fails[: args.max_fails]

    skill_dir = Path(args.skill) if args.skill else REPO / TEAM_DIR / args.domain
    skill_md = (skill_dir / "SKILL.md").read_text(encoding="utf-8") if (skill_dir / "SKILL.md").is_file() \
        else "(no current skill yet — this is the first round)"

    per_task = ["task | arm | score | passed"]
    for a in attempts:
        per_task.append(f"{a.get('task_name')} | {a.get('arm')} | {a.get('score')} | {a.get('passed')}")

    sections = [f"# Current SKILL.md\n{skill_md}",
                "# Per-task results (latest eval)\n" + "\n".join(per_task)]
    for i, row in enumerate(fails, 1):
        sections.append(f"# Failed trajectory {i} of {len(fails)}\n"
                        + assemble(row, args.domain, run_dir, 20))
    user_msg = "\n\n".join(sections)

    key = load_env_key("OPENAI_API_KEY")
    model = pick_model(key, args.model)
    pin, pout = price_for(model)
    worst = (len(user_msg) / 3.5) / 1e6 * pin + 8000 / 1e6 * pout
    if worst > args.cap:
        sys.exit(f"gpt_proposer: projected worst-case ${worst:.2f} exceeds cap ${args.cap:.2f} "
                 f"— reduce --max-fails")

    payload = {"model": model, "max_completion_tokens": 8000,
               "response_format": {"type": "json_object"},
               "messages": [{"role": "system", "content": SYSTEM},
                            {"role": "user", "content": user_msg}]}
    resp = api("https://api.openai.com/v1/chat/completions", key, payload)
    usage = resp.get("usage", {}) or {}
    cost = usage.get("prompt_tokens", 0) / 1e6 * pin + usage.get("completion_tokens", 0) / 1e6 * pout
    text = (resp.get("choices") or [{}])[0].get("message", {}).get("content", "") or ""
    try:
        files = json.loads(text).get("files") or {}
    except json.JSONDecodeError:
        sys.exit(f"gpt_proposer: model did not return valid JSON (cost ${cost:.4f})")
    if "SKILL.md" not in files:
        sys.exit(f"gpt_proposer: no SKILL.md in response (cost ${cost:.4f})")

    out = REPO / TEAM_DIR / f"{args.domain}-candidates" / f"{args.round}-{args.proposer}"
    out.mkdir(parents=True, exist_ok=True)
    for rel, content in files.items():
        rel_path = Path(rel)
        if rel_path.is_absolute() or ".." in rel_path.parts:
            print(f"  ! skipping unsafe path {rel!r}", file=sys.stderr)
            continue
        dest = out / rel_path
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(content, encoding="utf-8")
    n_lines = len(files["SKILL.md"].splitlines())
    print(f"wrote {out} ({len(files)} file(s); SKILL.md {n_lines} lines; model {model}; ${cost:.4f})")
    if n_lines > 40:
        print("  ! SKILL.md exceeds 40 lines — trim before evaluating", file=sys.stderr)


if __name__ == "__main__":
    main()
