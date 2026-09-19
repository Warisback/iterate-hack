# hle CHANGELOG

Kept outside the shipped skill folder so the learner never spends turns reading it.

## v1 (research priors, shipped in the early submission)
E1-E5 from the literature: fixed final block, one answer only, sandbox for math, never abstain, MC elimination.
Live leaderboard result with this version: 7.7%.

## v2 (shipped final) — rewritten from observed baseline evidence
Evidence from runs/hle-v0b trials:
- 2 of 4 baseline attempts produced NO /logs/agent/response.txt at all (reward None, no response file). A
  perfect answer never written scores zero — this is the dominant failure, not answer quality.
- The task's required field name is "Answer:", but v1's R1 mandated "Exact Answer:" (copied from the public
  HLE system prompt). v1 was instructing a format the grader does not ask for.
Changes:
- R1 rewritten: FIRST action is to write the response file with a current best answer, rewrite as reasoning
  improves. Mirrors the write-outputs-first rule that measurably helped qf.
- R2: use the exact field names the task states (Explanation / Answer / Confidence).
- R7 added: turn budget — by ~step 25 stop exploring, write the final file, finish.
- R3-R6 kept from v1 (one answer, sandbox math, never abstain, MC elimination).
