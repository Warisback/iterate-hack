---
name: banking-knowledge-tooling-and-termination
description: Prevents common banking-service failures: missing required DB write actions, tool/KB gating, and invalid termination.
---

R1: After start_conversation, decide whether the task requires a DB write action (e.g., apply_for_credit_card). If yes, you must execute the exact required write tool call before ending; do not stop after giving advice.
R2: Never invent product features, prices, limits, fees, or requirements. Every numeric/value claim must be supported by a KB_search result; if not found, say you can’t confirm and offer to search again.
R3: For any user request that implies an internal action or record change, run KB_search to discover the exact tool name + argument schema; only then call the tool. Do not guess tool names/args.
R4: When a KB-specified tool requires specific argument values (names, income, subscription flags, card type), collect them explicitly from the user and copy them verbatim into the tool call.
R5: If identity verification is required, complete the full verification flow per policy (collect 2 factors, verify via read tools, then call the verification logging tool) before accessing account-specific data; do not stop after merely requesting info.
R6: Only end the run via end_conversation tool, or by emitting exactly '###STOP###' as the entire final assistant message when the user has already stopped. Never end by returning an empty final answer.
R7: If a runtime/API error prevents progress, immediately send a brief message to the user acknowledging a technical issue and ask whether to retry or transfer; then either retry once or invoke transfer_to_human_agents per policy—do not silently terminate.