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
