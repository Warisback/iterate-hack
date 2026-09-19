---
name: qfbench-reliability-and-conventions
description: Prevents zero-output crashes, oversized tool calls, invented pricing formulas, off-by-one conventions, and exact-format CSV mismatches in quantitative-finance sandbox tasks graded by hidden file tests.
---

R1: First code action, before any data analysis: run one short python script that creates the output directory AND writes every output file the spec names — exact CSV header rows, and JSON files containing every required key with placeholder values. Refine values afterwards. A run can die on any turn; it must still leave all files on disk, because zero files means every test errors.

R2: Keep every tool call small. Create a file with a short skeleton first, then extend with str_replace edits of at most ~80 lines each; never emit a whole script in one giant call (oversized calls get truncated and fail tool validation). If a `create` fails because the file already exists, do NOT delete the file and retry — view it and continue with str_replace edits on it. A file-editor create needs BOTH `path` and `file_text` in the same call; a think call needs a single short `thought` string.

R3: Never `rm` a solution or output file. To replace one wholesale, write the new version at a different path (e.g. solve2.py), verify it exists and runs, then `mv` it over the old path. A delete-then-recreate gap plus one mid-run crash leaves nothing on disk.

R4: For standard derivative pricing — Black-Scholes, discrete geometric-Asian exact, Levy/two-moment, Curran geometric-conditioning — copy `formulas.py` from this skill folder into the workspace and import it. Do not re-derive these formulas from memory in prose.

R5: Before writing any pricing/metrics output, run sanity checks on every row (use `validate_asian_row` in formulas.py for Asian tasks): all option prices > 0, geometric <= arithmetic call, each approximation within a few standard errors of its own Monte Carlo estimate, and every bound the instruction states. If a check fails, fix the code before writing files — never ship a table you can see is broken.

R6: A count field takes its meaning from its NAME, not from nearby prose. A field named after prices/observations/days (e.g. n_prices) is the number of rows of the raw input series — data lines of the file, header excluded — even when the surrounding text says to report the number of returns; a return series always has exactly one fewer element than its price series. Verify the count with `wc -l` on the input file, never from a derived array.

R7: Apply exactly one day of signal lag, in exactly one place: a signal used on day t is built from data through day t-1. If the signal array is already constructed with that lag, index it with [t] at trade time — indexing [t-1] double-lags and guts the strategy's return.

R8: A trade/signal start-day parameter marks the FIRST event, not a waiting period: the first rebalance happens on trade_start_day itself, later rebalances at each subsequent period boundary, and metric windows begin there. Every provided parameter must visibly affect the result. If an integer checkpoint (e.g. a rebalance count) matches under one reading of an ambiguous rule, keep that reading — do not "fix" it away.

R9: When an output column is first_X_id / last_X_id over a set of rows, write the same primary identifier column of the first row and of the last row; never switch to different same-named fields inside the input record (e.g. use the first/last eligible trade's own trade id, not its constituent first_trade_id/last_trade_id fields).

R10: Exact-match file tests compare strings. Follow the stated float format literally (e.g. fixed 6 decimals on every float field), write empty strings exactly where told, keep the stated column and row order, and normalize tiny residuals with `round(x, 6) + 0.0` before formatting so "-0.000000" can never appear. Before finishing, re-read the output spec bullet-by-bullet against the actual written file.

R11: Grading reads only the output files. A final chat message, answer marker, or summary formatting changes nothing — never restructure or truncate file-writing work to satisfy message-format instructions.

R12: Exploration budget: at most ~5 short tool calls to inspect inputs (ls; then wc -l and a few head lines per file); never print whole data tables into chat. Then immediately write and RUN a first end-to-end version of the solution so every output file holds computed values while most of the turn budget still remains, and spend the rest refining with small str_replace edits and re-runs.
