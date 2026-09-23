# Run log

Starting Runware credits: $100 per CLAUDE.md — awaiting the exact balance the team reports; record it here.

## 2026-09-19 smoke (health, baseline, --limit 1)
- Result: FAILED on Docker ("Docker is not installed or not on PATH"), before any learner call.
- Auth: no auth error — the Runware key passed the price-fetch stage; full validation happens on the first learner call.
- Tokens: 0 · Cost: $0 · Balance change: none.
- Action: install WSL + Docker Desktop, rerun smoke test.
## report 2026-09-19 13:59

### smoke

domain **health** (healthbench) · learner `zai-glm-5-3-flash` · n_tasks 1 · note: pipeline_green_not_statistically_valid

| version | arm | rate | passes | learner tokens | learner cost | grader tokens | grader cost |
|---|---|---|---|---|---|---|---|
| smoke | baseline | 0.0411 | 0/1 | - | - | 36,947 | $0.0528 |
| smoke | **total** | | | 24,106 | $0.0013 | 50,412 | $0.0528 |

| task | baseline |
|---|---|
| healthbench-hard-00656524-cc51-47a3-bfb5-85e7096ee1c8 | 0.04 |

Failed or non-ok attempts (read these trajectories):
- `baseline` · healthbench-hard-00656524-cc51-47a3-bfb5-85e7096ee1c8 · score 0.04 · status ok · runs/smoke/harbor-jobs/healthbench-train-healthbench-hard-00656524-cc51-47a3-bfb5-85e7096ee1c8-b5dc96c7/task__f7uiMWH


## 2026-09-19 ~14:10 budget notes
- Budgets (user): qf $30 · health $30 · hle $40 · tau3 $50 · reserve $50 (holdout 17:15). Total $200.
- health-v0 first attempt CRASHED (Windows cp1252 encode of '≥' in harness final writes; fixed by PYTHONUTF8=1 on all future local runs). Results lost; spend NOT lost: learner 428k tok / $0.0267, grader 485k tok / $0.6714 → **$0.698 charged to health budget**.
- Running Runware spend so far: smoke $0.054 + crashed health $0.698 ≈ **$0.75**. health budget used: $0.75 of $30 (smoke was health-domain).
## report 2026-09-19 14:41

### health-v0

domain **health** (healthbench) · learner `zai-glm-5-3-flash` · n_tasks 8 · note: pipeline_green_not_statistically_valid

| version | arm | rate | passes | learner tokens | learner cost | grader tokens | grader cost |
|---|---|---|---|---|---|---|---|
| health-v0 | baseline | 0.2763 | 0/8 | - | - | 233,155 | $0.3255 |
| health-v0 | placebo | 0.3304 | 0/8 | - | - | 232,248 | $0.3254 |
| health-v0 | **total** | | | 378,318 | $0.0221 | 640,229 | $0.6509 |

| task | baseline | placebo |
|---|---|---|
| healthbench-hard-00656524-cc51-47a3-bfb5-85e7096ee1c8 | 0.16 | 0.25 |
| healthbench-hard-02109c83-28b1-4269-b4b2-5ceefb66524e | 0.49 | 0.40 |
| healthbench-hard-034d78e2-0873-4e4a-9621-735b51d0d020 | 0.03 | 0.79 |
| healthbench-hard-05bb23aa-3965-419a-a986-79c301d9270e | 0.00 | 0.00 |
| healthbench-hard-062e3a49-07e0-4b5c-a941-ceb8cc4111e4 | 0.30 | 0.10 |
| healthbench-hard-06902be5-32f0-4adc-ba00-e5ad2f98ea2d | 0.30 | 0.20 |
| healthbench-hard-08fdc56d-a23c-4b03-bfab-0e91a089c45c | 0.47 | 0.58 |
| healthbench-hard-09583fec-46bd-4a79-a524-94261baa875d | 0.45 | 0.32 |

Failed or non-ok attempts (read these trajectories):
- `baseline` · healthbench-hard-00656524-cc51-47a3-bfb5-85e7096ee1c8 · score 0.16 · status ok · runs/health-v0/harbor-jobs/healthbench-train-healthbench-hard-00656524-cc51-47a3-bfb5-85e7096ee1c8-fe3cbc95/task__RtoM6xK
- `baseline` · healthbench-hard-02109c83-28b1-4269-b4b2-5ceefb66524e · score 0.49 · status ok · runs/health-v0/harbor-jobs/healthbench-train-healthbench-hard-02109c83-28b1-4269-b4b2-5ceefb66524e-5f4b6b7d/task__fGgt9yC
- `baseline` · healthbench-hard-034d78e2-0873-4e4a-9621-735b51d0d020 · score 0.03 · status ok · runs/health-v0/harbor-jobs/healthbench-train-healthbench-hard-034d78e2-0873-4e4a-9621-735b51d0d020-077f5bb7/task__5sUeQcX
- `baseline` · healthbench-hard-05bb23aa-3965-419a-a986-79c301d9270e · score 0.00 · status ok · runs/health-v0/harbor-jobs/healthbench-train-healthbench-hard-05bb23aa-3965-419a-a986-79c301d9270e-8dea98a8/task__6vUosjH
- `baseline` · healthbench-hard-062e3a49-07e0-4b5c-a941-ceb8cc4111e4 · score 0.30 · status ok · runs/health-v0/harbor-jobs/healthbench-train-healthbench-hard-062e3a49-07e0-4b5c-a941-ceb8cc4111e4-9949b699/task__rAba2g5
- `baseline` · healthbench-hard-06902be5-32f0-4adc-ba00-e5ad2f98ea2d · score 0.30 · status ok · runs/health-v0/harbor-jobs/healthbench-train-healthbench-hard-06902be5-32f0-4adc-ba00-e5ad2f98ea2d-80be100c/task__brrvgSY
- `baseline` · healthbench-hard-08fdc56d-a23c-4b03-bfab-0e91a089c45c · score 0.47 · status ok · runs/health-v0/harbor-jobs/healthbench-train-healthbench-hard-08fdc56d-a23c-4b03-bfab-0e91a089c45c-4c15ccfd/task__FrPVKAT
- `baseline` · healthbench-hard-09583fec-46bd-4a79-a524-94261baa875d · score 0.45 · status ok · runs/health-v0/harbor-jobs/healthbench-train-healthbench-hard-09583fec-46bd-4a79-a524-94261baa875d-7ec125dd/task__VWohgdz
- `placebo` · healthbench-hard-00656524-cc51-47a3-bfb5-85e7096ee1c8 · score 0.25 · status ok · runs/health-v0/harbor-jobs/healthbench-train-healthbench-hard-00656524-cc51-47a3-bfb5-85e7096ee1c8-36aea027/task__9gemDQr
- `placebo` · healthbench-hard-02109c83-28b1-4269-b4b2-5ceefb66524e · score 0.40 · status ok · runs/health-v0/harbor-jobs/healthbench-train-healthbench-hard-02109c83-28b1-4269-b4b2-5ceefb66524e-4468abc0/task__rafidDD
- `placebo` · healthbench-hard-034d78e2-0873-4e4a-9621-735b51d0d020 · score 0.79 · status ok · runs/health-v0/harbor-jobs/healthbench-train-healthbench-hard-034d78e2-0873-4e4a-9621-735b51d0d020-e07c6a1b/task__vGzJvBf
- `placebo` · healthbench-hard-05bb23aa-3965-419a-a986-79c301d9270e · score 0.00 · status ok · runs/health-v0/harbor-jobs/healthbench-train-healthbench-hard-05bb23aa-3965-419a-a986-79c301d9270e-4fc4e5b2/task__MKg5VG4
- `placebo` · healthbench-hard-062e3a49-07e0-4b5c-a941-ceb8cc4111e4 · score 0.10 · status ok · runs/health-v0/harbor-jobs/healthbench-train-healthbench-hard-062e3a49-07e0-4b5c-a941-ceb8cc4111e4-804c8e2a/task__3VUDf6T
- `placebo` · healthbench-hard-06902be5-32f0-4adc-ba00-e5ad2f98ea2d · score 0.20 · status ok · runs/health-v0/harbor-jobs/healthbench-train-healthbench-hard-06902be5-32f0-4adc-ba00-e5ad2f98ea2d-1c276819/task__7nYpxAK
- `placebo` · healthbench-hard-08fdc56d-a23c-4b03-bfab-0e91a089c45c · score 0.58 · status ok · runs/health-v0/harbor-jobs/healthbench-train-healthbench-hard-08fdc56d-a23c-4b03-bfab-0e91a089c45c-27b04eeb/task__6dp6Z2S
- `placebo` · healthbench-hard-09583fec-46bd-4a79-a524-94261baa875d · score 0.32 · status ok · runs/health-v0/harbor-jobs/healthbench-train-healthbench-hard-09583fec-46bd-4a79-a524-94261baa875d-4aaa94f0/task__sQW3bh9


## 2026-09-19 15:50 health round 1 — first result
- r1-gpt-a: skill_rate 0.403 vs placebo 0.3304 (+0.073 dev, single run, noise unmeasured). Cost $0.33.
- Copied to submissions/denden/health/ as EARLY SUBMISSION candidate (user emails ~15:45). check-skill: pass.
- One task scored -0.40 under this skill (rubric negatives) — flag for round 2.

## health round 1 — full frontier (dev = 8 fixed tasks; baseline 0.2763 / placebo 0.3304)
health · r1 · best single gpt-a 0.403 (+0.073 vs placebo) · health spend ≈ $3.1 of $30 (incl. merge eval in flight)

| task | base | plac | gpt-a | gpt-b | claude-a | claude-b |
|---|---|---|---|---|---|---|
| 00656524 | 0.16 | 0.25 | **0.29** | 0.16 | 0.05 | -0.22 |
| 02109c83 | 0.49 | 0.40 | 0.33 | 0.29 | -0.11 | **0.48** |
| 034d78e2 | 0.03 | 0.79 | **0.85** | 0.71 | 0.29 | 0.71 |
| 05bb23aa | 0.00 | 0.00 | 0.45 | 0.23 | **0.48** | 0.34 |
| 062e3a49 | 0.30 | 0.10 | -0.40 | **0.47** | -0.12 | 0.28 |
| 06902be5 | 0.30 | 0.20 | **0.62** | 0.00 | 0.14 | 0.52 |
| 08fdc56d | 0.47 | 0.58 | 0.47 | **0.68** | 0.45 | 0.32 |
| 09583fec | 0.45 | 0.32 | **0.60** | 0.32 | 0.32 | 0.23 |

Scores: gpt-a 0.403 · gpt-b 0.359 · claude-b 0.331 · claude-a 0.188 (net harmful — dropped).
Survivors into merge: gpt-a (base, 4 unique wins) + gpt-b R8 clinician-triage (fixes gpt-a's -0.40) + claude-b R4 answer-first + claude-b R8 no-AI-meta. Merged = r1-merged (18 lines, check-skill pass), eval running.
EARLY SUBMISSION: submissions/denden/health = r1-gpt-a verbatim, check-skill pass.

## 16:40 checkpoints
- MERGED RESCORE: 0.4089 (run1 0.4457) -> same-skill run-to-run spread ~0.037; merged mean 0.427 = +0.097 vs placebo -> REAL (3x spread). Ship-candidate: r1-merged.
- ABLATION minus R6/R7: 0.3619 < both merged runs -> keep R6/R7 (claude-d's interference theory not confirmed at skill level).
- r2-gpt-c: 0.4074 ~ merged level, not better.
- qf-v0b BASELINE: baseline 0.25 (1/4: binance passes), placebo 0.00 (0/4 — placebo BROKE binance; format instruction harmful on code tasks). Learner $0.10, no grader. qf round-1 proposers launched (2 GPT + 1 Claude), screen on 2 tasks next.
- Health spend ≈ $6.8 of $30 · qf ≈ $0.9 of $30 · OpenAI ≈ $0.6.
- r2-claude-d (minimal 7): 0.3535 — below merged; minimal hypothesis rejected on aggregate (kept in frontier: best-of-round on 09583fec 0.52).
- SPILLOVER: merged on 3 fresh tasks = 0.3897 (dev mean 0.427) — generalizes, no revert.

## 16:52 health ROUND 2 CLOSED — ship = r1-merged
Final board: merged 0.446/0.409 (CONFIRMED) > gpt-d 0.420 > gpt-c 0.407 > claude-c 0.392 > ablate 0.362 > claude-d 0.354. Placebo 0.330.
submissions/denden/health = r1-merged (check-skill pass, tagged health-final-r1-merged). Holdout 17:15: baseline,placebo,skill on 8 holdout tasks.

## 17:00 EARLY SUBMISSION SET READY (tag early-submission-1)
- health: r1-merged — dev-CONFIRMED 0.446/0.409 vs placebo 0.330, spillover 0.390
- qf: r1-claude-a — PREDICTED best (trajectory forensics + validated formulas.py; screens still running)
- tau3: research-prior skill (T-rules; baseline still running; user owns tau3 — submitted per user instruction)
- hle: research-prior skill (E-rules; baseline still running)
All four pass check-skill. User emails; two submissions/day, this is #1.

## 17:55 endgame notes
- r3-general (de-overfit experiment): dev 0.2702 — BELOW placebo. Rejected; the removed rules carried real signal. health final = r1-merged, holdout pending.
- qf claude-a CONFIRMED 2/4 dev (fixed alpha-hedge, kept binance) vs baseline 1/4, placebo 0/4. qf final = r1-claude-a (already in folder).
- tau3 r2-merged (gpt-a + claude-a R9/R10) no-breakage screen on 006+007 running.

## 18:10 HEALTH HOLDOUT (scored once, never tuned on)
baseline 0.3868 · placebo 0.3992 · skill 0.5001 -> NET DELTA +0.1009. Consistent with dev (+0.10) and spillover. health SHIPS r1-merged.

## 18:20 FINAL SUBMISSION SET (tag final-submission)
- health: r1-merged — holdout net_delta +0.1009 (dev +0.08/+0.12, spillover consistent)
- qf: r1-claude-a + formulas.py — dev 2/4 vs baseline 1/4, placebo 0/4
- tau3: r1-gpt-a — screen-proven non-breaking; r2 merge reverted after it broke task-007 (db mismatch)
- hle: REWRITTEN answer-file-first (evidence: 2 of 4 baseline attempts died with no response.txt; task uses "Answer:" not "Exact Answer:"; qf-proven early-file rule). Shipped uneval'd — last place meant nothing to protect.
All four check-skill PASS.

## qf UPDATE: gpt-a confirm 2/2 (alpha-hedge 1.0, asian 1.0) -> gpt-a = 3/4 dev, DOMINATES claude-a 2/4. qf folder switched to r1-gpt-a (no formulas.py needed - it passed asian without it). r2-claude-a screen still running for comparison.

## 18:30 FINAL SUBMISSION VERIFIED (all four check-skill PASS, committed)
- health r1-merged | holdout +0.1009 (skill 0.500 / placebo 0.399 / baseline 0.387)
- qf r1-gpt-a | 3/4 dev (binance, alpha-hedge, asian) vs baseline 1/4, placebo 0/4
- tau3 r1-gpt-a | 4-task 0.50 = baseline, 2x placebo 0.25 (003/005 unsolved by every candidate)
- hle answer-file-first rewrite | validation still running at deadline
Post-deadline screens: qf r2-claude-a (13f fail, asian pass), qf r3-merged (13f fail, asian pass).
13f-amendment-aware-crowding unsolved by 4 distinct skills — crash + zero output files; needs a different
approach than prose rules (candidate: a skill-provided scaffold script that writes all spec outputs).

## post-deadline round (evening)
- tau3 r3 (shipped+R9 appended): 005 fail, 007 pass — rule IGNORED, learner died at step 4 in plain text again.
- tau3 r4 (channel rule FIRST, emphasised): 005 fail, 007 pass. Position hypothesis disproved.
- tau3 r5 (claude-a + post-transfer stop clause): 005 fail, 007 pass. THREE attempts: task-005's plain-text
  death is not fixable by prose for this learner. tau3 stays as shipped (r1-gpt-a).
- health r4-template (dispatch + section skeleton + D0 write-the-file rule): 0.404 vs merged band 0.409-0.446.
  Not an improvement; within noise of the low end. Health stays r1-merged.
  Worth keeping on the frontier: r4 scored 0.85 on 062e3a49 (best ever on the clinician task, merged got 0.47)
  and 0.64 on 06902be5, but collapsed on 08fdc56d (0.07 vs 0.47).
- KEY UNUSED FINDING (from holdout per-axis analysis, runs/health-holdout verdicts.json):
  our +0.10 comes ENTIRELY from context_awareness (0.419 vs placebo -0.246). On completeness — scored on 7 of
  8 tasks — we are BEHIND placebo (0.609 vs 0.652). And 1 of 8 holdout skill-arm tasks scored a hard 0 because
  the reply was never written to response.txt. Those are the two biggest remaining levers.
- Strategy change by user: qf switched to a no-op skill and hle to placebo-equivalent text, on the leaderboard
  observation that no-skill/placebo beat every participant in those domains (score = skill - placebo, so an
  inert skill lands ~0 and beats negative deltas). health keeps r1-merged (real +0.101 holdout gain);
  tau3 keeps r1-gpt-a.
