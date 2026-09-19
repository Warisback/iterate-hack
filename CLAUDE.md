# Aptura Self-Improving AI Hack: curator instructions

We write skills (submissions/<team>/<domain>/SKILL.md plus supporting files) that make a frozen learner, GLM 5.3 Flash in the OpenHands harness, better at four domains. Only the skill changes. Score = pass rate with our skill minus pass rate with a placebo skill, on private held-out tasks, averaged over qf, health, tau3, hle. We compete against Claude Fable 5.1 and Opus 5 curating autonomously. two humans on the team; you drive the loop, we read failures with you.

Team folder: submissions/denden/

## Domains
- qf: QuantitativeFinance-Bench, sandbox coding task, tests pass/fail. Cheap and fast. ~100M learner tokens.
- health: HealthBench, health conversation, model-graded rubric 0 to 1. Cheap and fast. ~100M.
- tau3: tau3-bench, serve a simulated customer via tool calls, assertions pass/fail. Slow, 4 to 8 GB RAM per task. ~300M.
- hle: Humanity's Last Exam, expert question, model-graded pass/fail. Slow. ~300M.

## Hard rules (a flagged skill scores zero)
- Learn from training tasks only. Never copy held-out content, rubrics or answer keys from the public source datasets. Do not search for the benchmark test sets or near-copies.
- Skill tools run offline inside the task container: no network, no API calls, no credentials, no URLs.
- Never edit hackathon.toml or src/skilltrainbench/. No effect on score, and discrepancies get flagged.
- Everything lives in submissions/denden/<domain>/. Run `uv run stbench check-skill submissions/denden/<domain>` before anything is submitted.
- Every eval spends Runware credits ($100 total). Default to --limit 5. Use --concurrency 1 for qf and tau3. Ask me before any run likely to cost more than $5. Read the token and cost lines every run and log them.
- Do not email or submit anything yourself. Prepare the folder, run check-skill, tell me it is ready.

## Commands
- Setup: uv sync; cp .env_example .env (RUNWARE_API_KEY); uv run stbench data pull; uv run stbench tasks --domain <d>
- Eval: uv run stbench eval --domain <d> --skill submissions/denden/<d> --arms baseline,placebo,skill --limit N --out runs/<d>-vN
- Read trajectories: uv run harbor view runs/<d>-vN/harbor-jobs, and runs/<d>-vN/attempts.jsonl
- Rerun specific tasks: --tasks name1,name2

## Method (follow in this order)
1. Harness before prompts. Build scripts/report.py that parses runs/*/eval_result.json and attempts.jsonl into one table (version, arm, score, tokens, cost, per-task pass/fail) and appends to runs/LOG.md. Split each domain's training tasks into dev (iterate) and holdout (5 to 8 tasks, scored once at end of day, never tuned on). Record the split in runs/SPLITS.md.
2. Baseline and placebo first. Then read every failed trajectory and bucket it: did not finish or wrong format; ignored an instruction; missing domain knowledge; arithmetic or code error; misread the task; tool misuse. Show bucket counts before writing any skill. Fix reliability buckets (finishing, format) before knowledge buckets; that is where most gains are.
3. Skill structure. SKILL.md is short: valid frontmatter, then numbered rules with stable ids (R1, R2...), one rule per failure bucket. Deeper material goes in separate files referenced from SKILL.md and read only when needed, so the learner does not burn turns on context it does not need. Never rewrite the whole skill; add and remove by rule id. Keep CHANGELOG.md per domain: rule ids changed, the failing trajectory that motivated it, before and after score.
4. Every proposed change must quote the failing trajectory behind it. No changes on intuition.
5. Where a bucket is arithmetic, units, formatting or validation, write a small offline script in the skill folder and tell the learner exactly when to call it. Deterministic tools beat prose for that class of error.
6. Noise discipline. Run candidates at least twice on small sets. If the delta is smaller than the run-to-run spread, it did not improve. Every few iterations, delete one rule and rescore; skills can make things worse.
7. Keep a frontier. If v3 wins on some tasks and v5 on others, keep both (git tag each version) and try merging the differing rules.
8. Generalise. If a rule only works because of one training item, remove it. We may write extra examples of the same shape ourselves; we may not pull public benchmark data.
9. Budget the day. health and qf until about 15:00. Then tau3 and hle using what we learned. Final holdout run on all four at about 17:00. Prepare an early submission around 14:00 (two leaderboard submissions per day, by email from us) and the final by 18:00. Close is 18:30.

## Starting hypotheses (test against real failures, do not assume)
- health: graders reward accuracy, completeness, asking a clarifying question when under-specified, tailoring to layperson vs clinician, clear emergency guidance when warranted, hedging without waffle; they penalise hallucinated specifics and length. Try a fixed response structure, an explicit "what is missing" step, and a hard emergency rule.
- qf: read the tests first, match signatures and output types exactly, print nothing extra, run the tests in the sandbox before finishing. A formulas reference file (bond pricing, NPV/IRR, Black-Scholes, day counts, compounding) plus a float-tolerance checklist.
- tau3: procedural failures: acting before confirming, not verifying identity, wrong tool argument formats, skipped policy steps, two actions when one was asked, not closing properly. Rules: read policy first, verify user, one tool call at a time, confirm before anything irreversible, repeat back exact values.
- hle: low absolute scores for this learner; aim for small reliable gains. Exact answer format, one final answer, no hedging between options, sandbox for any calculation. Do not spend most of the budget here.

## Runware smoke test (do before any eval)
- Confirm .env has RUNWARE_API_KEY set (do not print the key).
- Run: uv run stbench eval --domain health --arms baseline --limit 1 --out runs/smoke
- Confirm it completes, prints a token and cost line, and writes runs/smoke/eval_result.json. If it fails with an auth error, stop and tell me: the key is wrong. If it fails on Docker, stop and tell me.
- Read the Runware balance the team reports and record starting credits in runs/LOG.md. After every run, append tokens, cost and remaining balance.

## Reporting after every