# Research-backed rule candidates (compiled 2026-09-19 ~16:10, sources verified by research agent)

Cross-cutting: program-form skills beat prose for weak agents (ASI +11.3% over same-as-text, arXiv 2504.06821);
short step-sequences mined from OWN passing trajectories (AWM, arXiv 2409.07429); more skill text is NOT monotonic
(tau2 found an extra policy doc HURT — arXiv 2506.07982) -> keep ablating.

## health (HealthBench, arXiv 2505.08775 + 2509.02594)
- H1 ask 1-3 targeted questions AND give conditional answer — never questions alone, never skip asking (context-seeking = lowest-scoring theme)
- H2 completeness checklist: direct answer, causes/options, do-now, watch-for, when-to-seek-care (~40% of rubric items are completeness)
- H3 red-flag scan -> emergency-first sentence when triggered
- H4 no exact stats/doses unless certain; ranges/"commonly" (negative rubric points for hallucinated specifics)
- H5 register match: layperson vs clinician; obey explicit format requests exactly

## qf (SWE-agent 2405.15793, Self-Debugging 2304.05128, test-bias 2501.12793, PAL 2211.10435)
- Q1 read test file first; copy exact names/signatures/return types into skeleton
- Q2 run provided tests before finishing; fix and rerun until pass
- Q3 debug ONLY against provided tests; never self-invent expected values (test bias misleads weak models)
- Q4 return values, don't print; clean stdout before final run
- Q5 pricing/rate math via helpers.py formulas, compute in code never prose

## tau3 (tau-bench 2406.12045: wrong-args 33.3%, policy violations 25%, dropped requests 19.4%; IRMA 2508.20931; tau2 2506.07982; MANTRA 2605.06334)
- T1 read policy end-to-end first; write numbered applicable-rules checklist; check off before closing
- T2 copy tool args character-for-character from source; re-quote source line before each write call
- T3 state operation + all params, wait for explicit yes; one write per confirmation
- T4 list every distinct request at start; confirm each done/declined before closing
- T5 no transfer_to_human unless no tool exists; name the tool you'd use first

## hle (HLE 2501.14249)
- E1 fixed final block: Explanation / Exact Answer (answer only; MC = single letter) / Confidence N%
- E2 exactly one answer, never hedge between options
- E3 all multi-step math via sandbox Python, copy printed result
- E4 never abstain/refuse — best specific guess with low confidence (no wrong-answer penalty)
- E5 MC: eliminate provably-wrong first, pick among survivors
