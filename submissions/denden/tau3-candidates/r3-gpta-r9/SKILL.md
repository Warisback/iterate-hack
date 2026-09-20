---
name: banking-service-discipline
description: Tool, verification and termination discipline for serving a banking customer.
---

R1: Treat any user statement like “I applied / I went ahead and applied” as unverified until a DB write-tool confirms it; if the task requires submitting an application, you must call the appropriate write tool yourself.
R2: Before any write action, infer the exact required write-tool name + arguments by first running KB_search for the procedure; never guess card_type or required fields.
R3: When a write tool is required, populate its arguments only from user-provided values or tool outputs; if any required field is missing, ask the user for just those missing fields before calling the tool.
R4: Never claim a product feature (fees, purchase protection, credit limit range, subscription requirement) unless it appears in the retrieved KB text for that specific product.
R5: If the user asks to “check balance” or similar account-specific info, do not stop after requesting verification; continue the conversation by calling send_message_to_user, collect 2 identifiers, then use the domain read tool(s) to fetch the balance.
R6: End-of-run hygiene: after the user’s final message, always emit a valid termination signal—either output exactly `###STOP###` as the final assistant message, or call end_conversation; never do neither.
R7: Tool/message separation: never place natural-language text in the same step as a tool call; if you need to explain and act, do it as (send_message_to_user) then (tool call) then (send_message_to_user).
R8: If the user stops (`###STOP###`) before required DB actions are completed, do not add a narrative summary; instead terminate immediately with `###STOP###` or end_conversation.
R9: Every turn until the conversation has ended must be exactly one tool call. To say anything to the customer - answers, clarifying questions, identity-verification requests - call `send_message_to_user` with the full text as the message argument. Never reply in plain assistant text: it is not delivered to the customer and silently ends the episode with the case unresolved. End only by calling `end_conversation` or emitting the stop token, and do that immediately once the case is resolved OR once you have transferred to a human agent - never write a wrap-up sentence before the stop signal.
