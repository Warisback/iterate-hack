---
name: qfbench-reliability-and-conventions
description: Prevents zero-output crashes, oversized tool calls, invented pricing formulas, off-by-one conventions, and exact-format CSV mismatches in QuantitativeFinance-Bench sandbox tasks graded by hidden file tests.
---

R1: Create every required output file at its exact path early — write rough/placeholder values as soon as they are computable, then refine. A run that dies late must still leave all files on disk; zero files means every test errors.

R2: Keep every tool call small. Create a file with a short skeleton first, then extend with str_replace edits of at most ~80 lines each; never emit a whole script in one giant call (oversized calls get truncated and fail tool validation). A file-editor create needs BOTH `path` and `file_text` in the same call; a think call needs a single short `thought` string.

R3: Never delete a partial solution file until its replacement already exists on disk.

R4: For standard derivative pricing — Black-Scholes, discrete geometric-Asian exact, Levy/two-moment, Curran geometric-conditioning — copy `formulas.py` from this skill folder into the workspace and import it. Do not re-derive these formulas from memory in prose.

R5: Before writing any pricing/metrics output, run sanity checks on every row (use `validate_asian_row` in formulas.py for Asian tasks): all option prices > 0, geometric <= arithmetic call, each approximation within a few standard errors of its own Monte Carlo estimate, and every bound the instruction states. If a check fails, fix the code before writing files — never ship a table you can see is broken.

R6: Count conventions: "number of prices/observations" means rows of the raw series; a return series has exactly one fewer element. Recount from the input file, not from a derived array.

R7: Apply exactly one day of signal lag, in exactly one place: a signal used on day t is built from data through day t-1. If the signal array is already constructed with that lag, index it with [t] at trade time — indexing [t-1] double-lags and guts the strategy's return.

R8: A trade/signal start-day parameter marks the FIRST event, not a waiting period: the first rebalance happens on trade_start_day itself, later rebalances at each subsequent period boundary, and metric windows begin there. Every provided parameter must visibly affect the result. If an integer checkpoint (e.g. a rebalance count) matches under one reading of an ambiguous rule, keep that reading — do not "fix" it away.

R9: When an output column is first_X_id / last_X_id over a set of rows, write the same primary identifier column of the first row and of the last row; never switch to different same-named fields inside the input record (e.g. use the first/last eligible trade's own trade id, not its constituent first_trade_id/last_trade_id fields).

R10: Exact-match file tests compare strings. Follow the stated float format literally (e.g. fixed 6 decimals on every float field), write empty strings exactly where told, keep the stated column and row order, and normalize tiny residuals with `round(x, 6) + 0.0` before formatting so "-0.000000" can never appear. Before finishing, re-read the output spec bullet-by-bullet against the actual written file.

R11: Grading reads only the output files. A final chat message, answer marker, or summary formatting changes nothing — never restructure or truncate file-writing work to satisfy message-format instructions.
