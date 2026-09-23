# Team denden — Aptura Self-Improving AI Hack

Two humans + Claude Code as the curator, writing skills to improve a frozen learner
(GLM 5.3 Flash in the OpenHands harness) on four domains. Only the skill changes;
score = pass rate with our skill minus pass rate with a placebo skill, on private
held-out tasks.

## Results

| domain | submitted skill | evidence |
|---|---|---|
| health | `health/` (r1-merged, 13 rules) | **Holdout net +0.101** (skill 0.500 · placebo 0.399 · baseline 0.387), scored once on 8 untouched tasks. Consistent with dev (+0.10) and a 3-task spillover check (0.390). |
| qf | `qf/` (no-op, deliberate) | At deadline: r1-gpt-a, 3/4 dev tasks pass vs baseline 1/4, placebo 0/4. Switched post-deadline to a no-op after the live leaderboard showed placebo beating every participant's skill in qf — an inert skill lands ~0 and beats a negative delta. |
| tau3 | `tau3/` (r1-gpt-a) | 0.50 on the 4-task dev set = baseline, 2× placebo (0.25). Selected for proven no-breakage: the r2 merge was reverted on evidence after it broke a passing task. |
| hle | `hle/` (placebo-equivalent, deliberate) | At deadline: an answer-file-first rewrite motivated by 2/4 baseline attempts never writing `response.txt` at all. Switched post-deadline for the same leaderboard reason as qf. |

## Method

The loop, in order, for each domain:

1. **Harness before prompts.** `scripts/report.py` parses every run into one table
   (version, arm, score, tokens, cost, per-task pass/fail) and appends to
   `runs/LOG.md`. `scripts/make_splits.py` splits training tasks into dev
   (iterate freely) and holdout (scored once at end of day, never tuned on) by
   `md5(task_name)`; the split is frozen in `runs/SPLITS.md`.
2. **Baseline and placebo first**, then read every failed trajectory and bucket it
   (didn't finish / ignored instruction / missing knowledge / code error / misread
   task / tool misuse) before writing a single rule.
3. **Ensemble of proposers.** Each round, several candidate skills were drafted
   independently (GPT and Claude proposers), screened on the dev set, and the
   winners merged rule-by-rule. Rules have stable ids (R1, R2, ...) and every rule
   change quotes the failing trajectory that motivated it — see each domain's
   `*-candidates/CHANGELOG.md`.
4. **Noise discipline.** The same skill run twice on 8 health tasks scored
   0.446 / 0.409 — run-to-run spread ~0.04, so any delta under ~0.08 was treated
   as noise. Candidates were rescored before shipping.
5. **Ablate and de-overfit on evidence.** An ablation (merged minus R6/R7) scored
   worse, so both rules stayed. A "generalised" rewrite that deleted single-task
   rules scored *below placebo* and was rejected — the specific rules carried real
   signal.

## What worked

- **Reliability beats knowledge.** The biggest single finding: the learner often
  fails by never writing its answer where the grader looks (no `response.txt` in
  hle, zero output files in qf's hardest task, plain-text replies instead of
  `send_message_to_user` in tau3). Rules that force *write the deliverable first,
  in the exact expected format* outscored domain-knowledge rules.
- **Merging beats picking.** health's shipped skill is the best base candidate
  plus three rules grafted from losing candidates, each fixing a scored failure
  the base had (clinician escalate-first, answer-first, no AI meta-text).
- **A real holdout.** health's +0.101 was measured once, on tasks never used for
  tuning, and matched the dev estimate.

## What didn't

- **Prose can't fix everything.** tau3 task-005's plain-text death survived three
  differently-worded channel rules; qf's `13f` task defeated four distinct skills.
  Both need scaffold scripts, not sentences (see the post-deadline forensics in
  `tau3-candidates/CHANGELOG.md`).
- **More text is not more score.** Several longer, more "complete" candidates lost
  to the merged 13-liner, and the placebo itself *broke* a passing qf task.

## Folder map

- `<domain>/SKILL.md` — the submitted skill for that domain.
- `<domain>-candidates/` — the full frontier of candidate skills plus a
  `CHANGELOG.md` recording every rule change, its motivating trajectory, and
  before/after scores.
- `../../runs/LOG.md` — the timestamped run log (scores, tokens, cost per run).
- `../../runs/SPLITS.md` — the frozen dev/holdout split.
- `../../scripts/` — curator tooling: `report.py`, `make_splits.py`,
  `second_reader.py`, `gpt_proposer.py`.
