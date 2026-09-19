---
name: qf-bench-output-contracts
description: Prevent common QF-bench failures: strict output contracts, offline-only execution, and exact schema/format matching.
---
R1: Never leave the final answer empty; always emit a minimal completion message after writing files.
R2: Treat params/spec JSON fields as normative; use their names verbatim (e.g., if spec says target_quantity, map to required output key target_qty without inventing alternative inputs).
R3: Do not substitute signal definition/standardization; implement the alpha signal exactly as described (z-scored cross-sectionally, not ranks) and exclude the current day from lookback unless explicitly allowed.
R4: For monthly rebalancing, define rebalance days as the first available trading day of each calendar month within the trading window; do not approximate by fixed intervals.
R5: When a verifier is “semantic + checkpoints”, match every required intermediate/checkpoint field name and nesting exactly; do not add/omit/rename keys.
R6: For CSV deliverables with strict matching, reproduce exact column order, row order, and formatting rules; do not rely on “any order acceptable” unless explicitly stated.
R7: Enforce float formatting rules mechanically: CSV fixed 6 decimals for every float cell; JSON round to 6 decimals; do not emit empty strings where 0.000000 is required (or vice versa) unless specified.
R8: Enforce timestamp rules mechanically: epoch milliseconds as integers everywhere; never emit ISO strings; ensure 13-digit ms in CSV.
R9: In bucketed TCA, compute and emit all per-bucket quote-link fields exactly as required; if a bucket has zero child qty, still emit the row with the specified empty/zero conventions.
R10: If the runtime shows network/API errors, continue offline and still produce required output files; never abort due to remote LLM/URL fetch failures.
R11: For 13F reconstruction, write all required files even if internal checks fail; keep a cleaning audit that counts each rejected raw row once and only once.
R12: When amendments exist, resolve effective holdings by applying filings in chronological amendment order using amendment type semantics (restatement replaces; new holdings appends); record each applied filing in filing_resolution.
