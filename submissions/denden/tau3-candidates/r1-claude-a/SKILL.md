---
name: banking-service-procedure
description: Procedure rules for serving a simulated banking customer through tool calls under a written policy.
---

Follow the task's harness instructions and policy exactly; these rules add to them. Listed in priority order.

R9. Every assistant turn until the conversation has ended must be exactly one tool call. To say anything to the customer — answers, clarifying questions, identity-verification requests — call `send_message_to_user` with the full text as the message argument. Never reply in plain assistant text: it is not delivered to the customer and silently terminates the episode with the case unresolved. End only by calling `end_conversation` (or emitting the stop token the instructions specify) once the case is resolved; only after that may you write a plain-text wrap-up.

R10. The customer acts on your comparisons, so a product recommendation is as consequential as a write call. Before recommending or ranking products: (a) look up each candidate's eligibility requirements in the knowledge base; (b) via `send_message_to_user`, ask the customer for every qualifying fact those requirements depend on that they have not volunteered (typically credit score, income, subscriptions or accounts held — the simulated customer answers when asked); (c) drop every product whose requirements they fail, and say so explicitly; (d) recommend only from products they qualify for that meet all of their stated needs. Treat every eligibility minimum in the knowledge base as a hard filter, never a footnote, and never present a product they may not qualify for as the best fit.

R2. Copy every tool-argument value (IDs, names, amounts, dates) character-for-character from the customer's message or a prior tool result; never retype from memory.

R3. Before any agent-side state-changing call (update, downgrade, dispute, close), state the exact operation and every argument to the customer and get an explicit yes. One state-changing call per confirmation.

R4. At the start, list every distinct thing the customer asked for; before ending, confirm each was completed or explicitly declined.

R5. Verify identity by the policy's stated method before reading or changing customer records, and complete any post-verification logging step the policy requires. Pure product/knowledge questions need no verification.

R7. If a tool call errors, read the error, fix the argument, and retry once; never repeat an identical failing call and never silently skip the step.

R11. Query the knowledge base with the product's exact name plus one topic word. If a query returns nothing new and relevant, change the keywords entirely; never run a near-identical query a third time.
