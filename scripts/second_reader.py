#!/usr/bin/env python3
"""Second reader: independent OpenAI diagnosis of failed skill-arm attempts.

Curator-side only (lives in scripts/, never inside submissions/ — skills must
run offline). For each FAILED attempt in one arm of a run it assembles a
compact trajectory (task instruction, last turns of the learner, final answer,
grader verdict / failing tests — never the skill text) and asks an OpenAI
model, one independent call per failure, for a one-line cause and one
preventive rule. Results are cached per attempt in <run>/second_reader.json,
then merged with the curator's own buckets (<run>/curator_diagnosis.json,
which MUST be written first) into <run>/diagnosis.md.

Usage:
    uv run python scripts/second_reader.py runs/qf-v3            # skill arm
    uv run python scripts/second_reader.py runs/qf-v0 --arm baseline
    ... --cap 1.50 --model gpt-5.1 --max-turns 20 --dry-run

The curator column comes from <run>/curator_diagnosis.json:
    {"<task_name>": {"bucket": "...", "rule": "..."}, ...}
The script refuses to call OpenAI while that file is missing, so the curator's
diagnosis is always on disk first and cannot be influenced by the model's.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
import tomllib
import urllib.error
import urllib.request
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent

PROMPT = (
    "You are reviewing one failed attempt by a coding agent. State the single "
    "most likely cause of failure in one line, then one concrete instruction "
    "that would have prevented it, phrased as a rule the agent can follow. "
    "No preamble. Format: CAUSE: ... / RULE: ..."
)

# Strongest reasoning first among models our credits plausibly allow at the
# $-per-failure this cap implies. '-pro' tiers are excluded on purpose: one
# call would eat most of the $1.50 run cap.
MODEL_PREFERENCE = ("gpt-5.2", "gpt-5.1", "gpt-5", "o3", "o4-mini", "gpt-5-mini", "gpt-4.1")
# USD per 1M tokens (input, output); unknown models get a conservative guess.
PRICES = {"gpt-5.2": (3.0, 24.0), "gpt-5.1": (1.25, 10.0), "gpt-5": (1.25, 10.0),
          "o3": (2.0, 8.0), "o4-mini": (1.1, 4.4), "gpt-5-mini": (0.25, 2.0),
          "gpt-4.1": (2.0, 8.0)}
DEFAULT_PRICE = (5.0, 25.0)
MAX_OUTPUT_TOKENS = 4000  # includes reasoning tokens
TRAJ_CHAR_CAP = 28_000

SKILL_MARKERS = ("stbench-skill", "SKILL.md", "skill.md")
REDACTED = "[redacted: skill content is never shown to the second reader]"


def die(msg: str) -> None:
    sys.exit(f"second_reader: {msg}")


def load_env_key(name: str) -> str:
    env = REPO / ".env"
    if not env.is_file():
        die(".env not found")
    for line in env.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith(f"{name}=") and len(line) > len(name) + 1:
            return line.split("=", 1)[1].strip().strip('"')
    die(f"{name} not set in .env")
    raise AssertionError


def read_text_any(path: Path) -> str:
    # the harness writes jsonl without an encoding arg -> cp1252 on Windows
    data = path.read_bytes()
    try:
        return data.decode("utf-8")
    except UnicodeDecodeError:
        return data.decode("cp1252", errors="replace")


def read_jsonl(path: Path) -> list[dict]:
    rows = []
    if path.is_file():
        for line in read_text_any(path).splitlines():
            line = line.strip()
            if line:
                try:
                    rows.append(json.loads(line))
                except json.JSONDecodeError:
                    pass
    return rows


def api(url: str, key: str, payload: dict | None = None, timeout: int = 300) -> dict:
    req = urllib.request.Request(
        url, data=json.dumps(payload).encode() if payload is not None else None,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        method="POST" if payload is not None else "GET")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return json.loads(r.read().decode())
    except urllib.error.HTTPError as e:
        body = e.read().decode(errors="replace")[:400]
        raise RuntimeError(f"OpenAI API {e.code}: {body}") from None


def pick_model(key: str, override: str | None) -> str:
    if override:
        return override
    ids = {m.get("id", "") for m in api("https://api.openai.com/v1/models", key).get("data", [])}
    for want in MODEL_PREFERENCE:
        if want in ids:
            return want
        dated = sorted(i for i in ids if i.startswith(want + "-") and not any(
            x in i for x in ("pro", "audio", "realtime", "search", "image", "codex", "chat")))
        if dated:
            return dated[-1]
    die("no known reasoning model available on this OpenAI key; pass --model")
    raise AssertionError


def price_for(model: str) -> tuple[float, float]:
    # longest name first, so gpt-5-mini never matches the gpt-5 price
    for name in sorted(PRICES, key=len, reverse=True):
        if model == name or model.startswith(name + "-"):
            return PRICES[name]
    return DEFAULT_PRICE


def truncate_block(text: str, keep: int = 30) -> str:
    lines = text.splitlines()
    if len(lines) <= 2 * keep:
        return text
    return "\n".join(lines[:keep] + [f"... [{len(lines) - 2 * keep} lines truncated] ..."] + lines[-keep:])


def redact(text: str) -> str:
    """Drop any content that carries the skill text; diagnose behaviour, not our rules."""
    if any(m in text for m in SKILL_MARKERS):
        kept = [ln if not any(m in ln for m in SKILL_MARKERS) else f"  {REDACTED}"
                for ln in text.splitlines()]
        # a marker line usually introduces the skill body: cut everything after
        # the first marker inside one block to be safe
        for i, ln in enumerate(kept):
            if REDACTED in ln:
                return "\n".join(kept[: i + 1])
        return "\n".join(kept)
    return text


_SKILL_BODY_RE = re.compile(r"^\s*---\s*\n\s*name\s*:.*?\n.*?description\s*:", re.S | re.M)
_OBS_KEYS = ("observation", "output", "result")


def _fmt_event(ev: dict) -> str | None:
    """Best-effort render of one agent event (OpenHands-ish shapes) — all fields."""
    role = ev.get("role") or ev.get("source") or ev.get("type") or "event"
    if role == "system":  # agent scaffolding, not learner behaviour
        return None
    parts = []
    for k in ("thought", "content", "message", "text", "action", "command", "code",
              "args", "arguments", "path", "observation", "output", "result"):
        v = ev.get(k)
        if isinstance(v, (dict, list)):
            v = json.dumps(v, ensure_ascii=False)
        if isinstance(v, str) and v.strip():
            parts.append(f"{k}: {truncate_block(v.strip())}")
    return f"[{role}] " + "\n".join(parts) if parts else None


def _looks_like_skill_body(text: str) -> bool:
    return any(m in text for m in SKILL_MARKERS) or bool(_SKILL_BODY_RE.search(text))


def gather_turns(trial_dir: Path, max_turns: int) -> str:
    """Last `max_turns` learner events from the trial's agent logs, tolerant of layout."""
    agent_dir = trial_dir / "agent"
    if not agent_dir.is_dir():
        return "[no agent log directory in this trial]"
    events: list[str] = []
    files = [p for p in sorted(agent_dir.rglob("*"))
             if p.is_file() and p.stat().st_size < 20_000_000
             and not any(m in str(p) for m in SKILL_MARKERS)
             and p.name != "response.txt"]
    raw_events: list[dict] = []
    for p in (p for p in files if p.suffix in (".jsonl", ".ndjson")):
        raw_events.extend(read_jsonl(p))
    for p in (p for p in files if p.suffix == ".json"):
        # harbor writes agent/trajectory.json: {"steps": [{source, message}, ...]}
        try:
            d = json.loads(read_text_any(p))
        except json.JSONDecodeError:
            continue
        steps = d.get("steps") if isinstance(d, dict) else d
        if isinstance(steps, list):
            raw_events.extend(ev for ev in steps if isinstance(ev, dict))
    redact_next_obs = False
    for ev in raw_events:
        line = _fmt_event(ev)
        if not line:
            continue
        is_obs = any(isinstance(ev.get(k), str) and ev[k].strip() for k in _OBS_KEYS)
        if _looks_like_skill_body(line) or (redact_next_obs and is_obs):
            # a skill read plus the observation that answers it: drop both
            redact_next_obs = not (redact_next_obs and is_obs)
            events.append(REDACTED)
            continue
        events.append(line)
    if len(events) < 3:  # empty/thin trajectory: pull in the plain logs too
        logs = sorted((p for p in files if p.suffix in (".log", ".txt", ".out")),
                      key=lambda p: p.stat().st_size, reverse=True)[:3]
        for p in logs:
            try:
                events.append(f"[file {p.name}]\n"
                              + redact(truncate_block(p.read_text(encoding='utf-8', errors='replace'), 60)))
            except OSError:
                continue
    if not events:
        return "[no readable agent logs in this trial]"
    out = "\n\n".join(events[-max_turns:])
    if len(out) > TRAJ_CHAR_CAP:
        out = out[-TRAJ_CHAR_CAP:]
    return out


def gather_verdict(trial_dir: Path) -> str:
    parts = []
    result = trial_dir / "result.json"
    if result.is_file():
        try:
            vr = json.loads(result.read_text(encoding="utf-8")).get("verifier_result")
            if vr is not None:
                parts.append("verifier_result: " + truncate_block(json.dumps(vr, ensure_ascii=False, indent=1)))
        except (OSError, json.JSONDecodeError):
            pass
    vdir = trial_dir / "verifier"
    if vdir.is_dir():
        for p in sorted(vdir.rglob("*")):
            if p.is_file() and p.stat().st_size < 200_000 and not any(m in str(p) for m in SKILL_MARKERS):
                try:
                    txt = p.read_text(encoding="utf-8", errors="replace").strip()
                except OSError:
                    continue
                if txt:
                    block = f"[verifier/{p.relative_to(vdir)}]\n{truncate_block(txt)}"
                    parts.append(REDACTED if _looks_like_skill_body(block) else block)
    return "\n\n".join(parts) if parts else "[no grader/verifier output found]"


def instruction_for(task_name: str, domain: str) -> str:
    cfg = tomllib.loads((REPO / "hackathon.toml").read_text(encoding="utf-8"))
    local = cfg.get("data", {}).get("local_dir", "dataset/hackathon")
    ddir = cfg.get("domains", {}).get(domain, {}).get("dataset_dir", f"{local}/{domain}/tasks")
    p = REPO / ddir / task_name / "instruction.md"
    if p.is_file():
        return truncate_block(p.read_text(encoding="utf-8", errors="replace"), 60)
    return "[instruction.md not found for this task]"


def assemble(row: dict, domain: str, run_dir: Path, max_turns: int) -> str:
    task = row.get("task_name") or row.get("task_id", "?")
    trial = row.get("trial_dir")
    trial_dir = Path(trial) if trial else None
    if trial_dir is not None and not trial_dir.is_absolute():
        trial_dir = REPO / trial_dir
    turns = gather_turns(trial_dir, max_turns) if trial_dir and trial_dir.is_dir() else "[trial dir missing]"
    verdict = gather_verdict(trial_dir) if trial_dir and trial_dir.is_dir() else "[trial dir missing]"
    answer = (row.get("answer") or "").strip() or "[empty]"
    return (f"# Task instruction\n{instruction_for(task, domain)}\n\n"
            f"# Learner trajectory (last {max_turns} events, long outputs truncated)\n{turns}\n\n"
            f"# Final answer\n{truncate_block(answer)}\n\n"
            f"# Grader verdict / failing tests\nscore={row.get('score')} status={row.get('status')}\n{verdict}")


def call_openai(key: str, model: str, trajectory: str) -> tuple[str, dict]:
    payload = {"model": model, "max_completion_tokens": MAX_OUTPUT_TOKENS,
               "messages": [{"role": "system", "content": PROMPT},
                            {"role": "user", "content": trajectory}]}
    try:
        resp = api("https://api.openai.com/v1/chat/completions", key, payload)
    except RuntimeError as e:
        if "max_completion_tokens" in str(e) or "unsupported" in str(e).lower():
            payload.pop("max_completion_tokens", None)
            resp = api("https://api.openai.com/v1/chat/completions", key, payload)
        else:
            raise
    text = (resp.get("choices") or [{}])[0].get("message", {}).get("content", "") or ""
    return text.strip(), resp.get("usage", {}) or {}


def parse_cause_rule(text: str) -> tuple[str, str]:
    cause = rule = ""
    m = re.search(r"CAUSE:\s*(.+?)(?:\n|/\s*RULE:|$)", text, re.S)
    if m:
        cause = " ".join(m.group(1).split())
    m = re.search(r"RULE:\s*(.+)", text, re.S)
    if m:
        rule = " ".join(m.group(1).split())
    return cause or " ".join(text.split())[:200], rule


BUCKETS = {
    "did-not-finish/format": ("finish", "format", "cutoff", "truncat", "incomplete", "ran out",
                              "turn limit", "iteration", "empty", "no final", "never submitted",
                              "did not complete", "timeout"),
    "ignored-instruction": ("ignore", "instruction", "requirement", "despite", "failed to follow",
                            "policy", "asked for", "explicitly"),
    "missing-knowledge": ("knowledge", "formula", "concept", "domain", "wrong method",
                          "wrong approach", "incorrect model", "convention", "definition"),
    "arithmetic/code-error": ("arithmetic", "calculation", "numeric", "off-by", "bug", "code error",
                              "exception", "syntax", "rounding", "precision", "sign", "unit",
                              "logic error", "implementation error"),
    "misread-task": ("misread", "misinterpret", "misunderstood", "wrong question",
                     "different task", "wrong problem"),
    "tool-misuse": ("tool", "command", "argument", "wrong file", "path", "edit fail",
                    "call", "api misuse"),
}


def classify(text: str) -> str | None:
    low = text.lower()
    scores = {b: sum(1 for k in kws if k in low) for b, kws in BUCKETS.items()}
    best = max(scores, key=lambda b: scores[b])
    return best if scores[best] > 0 else None


def flag(cur: dict | None, cause: str, rule: str) -> str:
    cur_text = f"{(cur or {}).get('bucket', '')} {(cur or {}).get('rule', '')}".strip()
    sr_text = f"{cause} {rule}".strip()
    cur_b = classify(cur_text) if cur_text else None
    sr_b = classify(sr_text) if sr_text else None
    cur_specific = bool(cur_text and (cur or {}).get("rule"))
    sr_specific = bool(rule)
    if cur_b and sr_b and cur_b == sr_b:
        return "AGREE"
    if cur_specific != sr_specific or (cur_b is None) != (sr_b is None):
        return "ONE-SIDED"
    if cur_b and sr_b:
        return "DISAGREE"
    return "ONE-SIDED"


def md_escape(s: str) -> str:
    return s.replace("|", "\\|").replace("\n", " ")


def main() -> None:
    ap = argparse.ArgumentParser(description="Second-reader diagnosis of failed attempts")
    ap.add_argument("run", help="run folder, e.g. runs/qf-v3")
    ap.add_argument("--arm", default="skill", help="arm to diagnose (default: skill)")
    ap.add_argument("--cap", type=float, default=1.50, help="max USD spend for this run (default 1.50)")
    ap.add_argument("--model", default=None, help="override model id")
    ap.add_argument("--max-turns", type=int, default=20, help="trajectory events to include (15-20)")
    ap.add_argument("--dry-run", action="store_true", help="assemble trajectories, no API calls")
    args = ap.parse_args()

    run_dir = Path(args.run)
    if not run_dir.is_absolute():
        run_dir = REPO / run_dir
    if not run_dir.is_dir():
        die(f"run folder not found: {run_dir}")

    attempts = read_jsonl(run_dir / "attempts.jsonl")
    if not attempts:
        die(f"no attempts in {run_dir / 'attempts.jsonl'}")
    failures = [a for a in attempts if a.get("arm") == args.arm and a.get("passed") is False]
    skipped = [a for a in attempts if a.get("arm") == args.arm and a.get("passed") is None]
    if skipped:
        print(f"note: {len(skipped)} ungraded attempt(s) in arm {args.arm!r} skipped (passed=None)")
    if not failures:
        die(f"no failed attempts in arm {args.arm!r} — the second reader only reads failures")

    curator_path = run_dir / "curator_diagnosis.json"
    if not curator_path.is_file():
        die(f"{curator_path} missing. Write your own buckets to disk FIRST "
            '({"<task_name>": {"bucket": "...", "rule": "..."}}), then rerun.')
    curator = json.loads(curator_path.read_text(encoding="utf-8"))

    try:
        result = json.loads((run_dir / "eval_result.json").read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        result = {}
    domain = result.get("domain") or run_dir.name.split("-")[0]

    cache_path = run_dir / "second_reader.json"
    cache = json.loads(cache_path.read_text(encoding="utf-8")) if cache_path.is_file() else {}

    key = load_env_key("OPENAI_API_KEY")
    model = None
    if not args.dry_run:
        model = pick_model(key, args.model)
        pin, pout = price_for(model)
        print(f"second reader model: {model} (assumed ${pin}/M in, ${pout}/M out) · cap ${args.cap:.2f}/run")

    spent = sum(v.get("cost", 0.0) for v in cache.values())
    rows = []
    for row in failures:
        task = row.get("task_name") or row.get("task_id", "?")
        akey = f"{row.get('task_id', task)}|{args.arm}"
        traj = assemble(row, domain, run_dir, args.max_turns)
        if args.dry_run:
            print(f"--- {task} ({len(traj)} chars) ---\n{traj[:1200]}\n...")
            continue
        if akey in cache:
            entry = cache[akey]
        else:
            pin, pout = price_for(model)
            worst = (len(traj) / 3.5) / 1e6 * pin + MAX_OUTPUT_TOKENS / 1e6 * pout
            if spent + worst > args.cap:
                print(f"WARNING: stopping — next call could take spend past ${args.cap:.2f} "
                      f"(spent ${spent:.4f}); remaining failures not diagnosed", file=sys.stderr)
                break
            text, usage = call_openai(key, model, traj)
            cost = (usage.get("prompt_tokens", 0) / 1e6) * pin + (usage.get("completion_tokens", 0) / 1e6) * pout
            spent += cost
            cause, rule = parse_cause_rule(text)
            entry = {"model": model, "cause": cause, "rule": rule, "raw": text,
                     "usage": usage, "cost": round(cost, 6)}
            cache[akey] = entry
            cache_path.write_text(json.dumps(cache, indent=2, ensure_ascii=False), encoding="utf-8")
            print(f"  {task}: ${cost:.4f} (total ${spent:.4f})")
        cur = curator.get(task) or curator.get(row.get("task_id", ""))
        rows.append((task, cur, entry))

    if args.dry_run:
        return

    lines = [f"# Second-reader diagnosis — {run_dir.name}", "",
             f"Arm: {args.arm} · model: {model} · {len(rows)} of {len(failures)} failures diagnosed "
             f"· OpenAI spend this run: ${spent:.4f} (cap ${args.cap:.2f})", "",
             "| task | curator: bucket / rule | second reader: cause / rule | flag |",
             "|---|---|---|---|"]
    for task, cur, entry in rows:
        cur_txt = f"**{cur['bucket']}** — {cur.get('rule', '')}" if cur else "*(no curator entry)*"
        sr_txt = f"CAUSE: {entry['cause']} / RULE: {entry['rule'] or '(none)'}"
        lines.append(f"| {md_escape(task)} | {md_escape(cur_txt)} | {md_escape(sr_txt)} "
                     f"| {flag(cur, entry['cause'], entry['rule'])} |")
    out = run_dir / "diagnosis.md"
    out.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
