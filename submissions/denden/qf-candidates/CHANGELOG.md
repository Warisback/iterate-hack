# qf skill changelog (curator notes — not part of any submitted skill folder)

## r2-claude-a (from r1-claude-a)

Base: r1-claude-a, dev 2/4 (PASS binance-btc-participation-tca, alpha-hedge-strategy; FAIL 13f-amendment-aware-crowding, asian-option-levy-curran). formulas.py unchanged (smoke-tested after copy: geo 5.9402 / levy 6.1742 / curran 6.1556 vs MC 6.1409±0.0599, validate_asian_row -> no violations).

### R6 revised — motivated by asian-option-levy-curran WITH-skill failure
Trajectory: runs/qf-r1-claude-a-confirm/harbor-jobs/qfbench-train-asian-option-levy-curran-ccc9703f/task__6HWeNeY
- Verifier: 24/25 passed; only failure `TestCalibration::test_n_prices: n_prices=692, expected 693` (score 0 — all-or-nothing).
- The task prose says "Report: Number of log-returns" but the output field is named `n_prices`; hidden test asserts the raw close-price row count. Learner had old R6 in context (log line 406) and formulas.py imported, yet planned "calibration.json: n_prices = number of log-returns" (log line 937) and wrote 692 (line 1594).
- Fix: R6 now states the field NAME wins over nearby prose ("even when the surrounding text says to report the number of returns"), returns = prices - 1, verify via wc -l on the input file.
- Skill already fixed the baseline's second failure (test_all_prices_positive failed in runs/qf-v0b asian 4c63cb3e; passes with skill), so R4/R5 kept verbatim.

### R1/R2/R3 strengthened + R12 added — motivated by 13f WITH-skill failure
Trajectory: runs/qf-r1-claude-a-screen/harbor-jobs/qfbench-train-13f-amendment-aware-crowding-d0031f59/task__XbyHd8g
- Verifier: all tests ERROR, `FileNotFoundError: /app/output/filing_resolution.csv` — ZERO of the 8 required output files existed (baseline v0b at least wrote some: 11 failed / 40 errors).
- Sequence in agent/openhands_sdk.txt: ~15 exploration/analysis actions incl. dumping whole TSV tables (320K cumulative input tokens); mkdir output but no files; created solve.py skeleton; one big str_replace; then "Rewrite solution script with full pipeline" via `create` on the existing path -> "Cannot overwrite files using command create"; then `rm /app/solution/solve.py` (log line ~2641, violating old R3); the very next LLM completion died with litellm APIError and the conversation crashed. Nothing on disk.
- Fixes: R1 now mandates writing every spec-named output file (headers + full JSON keys) as the FIRST code action; R2 adds "if create fails because the file exists, never delete-and-retry — continue with str_replace"; R3 becomes mechanical (never rm; write solve2.py then mv over); new R12 caps exploration at ~5 short calls, bans printing whole tables, and requires an early end-to-end run so a mid-run crash still leaves computed files.

### Unchanged: R4, R5, R7, R8, R9, R10, R11 (R7/R8 back alpha-hedge-strategy pass; R9/R10/R11 back binance-btc-participation-tca pass). Rule ids stable.

Scores: before = 2/4 dev (r1-claude-a screen+confirm). After = not yet run.
