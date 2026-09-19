# tau3 CHANGELOG

Kept outside the shipped skill folder so the learner never spends turns reading it.

## v0 baseline (dev = 4 tasks): baseline 0.50 (passes 006, 007) · placebo 0.25
Placebo's 007 failure was an infra crash (litellm APIError at step 0, step_count=0, no trajectory), NOT a
behavioural failure, so the true placebo bar is likely ~0.50.

## Diagnosed failures (from trajectories + verifier)
- task-005, BOTH arms: the learner answered in plain assistant text instead of calling send_message_to_user.
  A text-only turn ends the episode; verifier recorded "Runtime ended without a valid tau2 stop signal",
  trajectory_message_count=2. Correct intent, wrong channel.
- task-003, BOTH arms: recommended a card the customer did not qualify for without ever asking credit score or
  income; expected DB state was an application for a different card. Also 5-7 near-identical KB searches.

## r1 candidates (screened on 2 tasks each)
- gpt-a: 003 fail, 007 PASS. gpt-b: 003 fail, 007 PASS. claude-a (channel-fix R9 + eligibility R10): 003 fail, 005 fail.
- Nobody fixed 003 or 005. Selection therefore = "does not break what works".

## r2-merged (gpt-a + claude-a R9,R10) -> REVERTED
No-breakage screen on the two passing tasks: 006 PASS, 007 FAIL (db_match false). The grafted rules broke a
working task, so the merge was discarded on evidence.

## FINAL: r1-gpt-a (frontmatter name/description scrubbed of benchmark references)

## POST-DEADLINE FORENSICS on r1-claude-a (do this first next round)
R9 (always speak via send_message_to_user) WORKED and is worth keeping:
- v0: both arms on task-005 died at turn 2 answering in plain text (trajectory_message_count 2).
- With R9: every conversational turn was exactly one tool call; the episode reached 12 messages, 11 steps,
  num_errors 0. The channel bucket is fixed.
Task-005 still scored 0 for a DIFFERENT, narrower reason: after transfer_to_human_agents succeeded the learner
wrote a plain-text wrap-up without calling end_conversation or emitting ###STOP###. Verifier:
"Runtime ended without a valid tau2 stop signal. termination_reason=None", tau2_evaluation=false — the DB
reward was never computed. end_conversation WAS an available tool. R9's wording gates ending on "once the case
is resolved", which does not obviously cover a transfer-to-human.
FIX for next round (one sentence added to R9):
  "After transfer_to_human_agents, immediately call end_conversation or emit ###STOP### before any wrap-up text."
Task-003 failed substantively, not on protocol: terminated cleanly and was evaluated, but the learner
recommended Platinum/Gold while ground truth expected an application for the Silver Rewards Card. R10 half
worked (it did ask about subscription and credit score). R11 was flagrantly violated: 18 consecutive KB_search
calls, mostly near-identical rephrasings, burning ~1.04M of the run's prompt tokens — enforce the
no-repeat-query cap mechanically next time.
