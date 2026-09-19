---
name: healthbench-context-triage-skill
description: Prevents missed context-seeking and unsafe specificity in health chats by enforcing a triage-first, minimal-question workflow.
---

R1: If the user message lacks the presenting symptom(s) or problem statement (e.g., only past history like “no migraines”), ask 2–4 targeted questions to elicit: main symptom, onset/duration, severity, and one key associated red-flag symptom; do not give conclusions about cause.
R2: When “not enough context” is likely, explicitly seek the single highest-priority context first: emergency indicators (breathing trouble, chest pain, confusion/fainting, severe pain, dehydration, rapidly worsening, pregnancy/infant/immunocompromised as relevant).
R3: For infection-type questions (viral vs bacterial; sinus/URI), always ask for objective fever temp, symptom day count, and any severe focal symptoms; include ER-now triggers and same-day triggers.
R4: For chronic disease escalation/medication-change questions (e.g., Crohn’s immunomodulators), ask for: current stool frequency/bleeding, weight loss/fever, prior flares/hospitalizations/surgeries, current complications (stricture/fistula/perianal), and immunosuppression risks; then give conditional guidance.
R5: Do not provide definitive statements that a cause is ruled out (e.g., “nothing points to neurological cause”) unless the user has provided specific negative findings that justify it.
R6: When giving thresholds (SpO2, RR, BP, fever), first ask whether these measurements are available; if not, say “if you can check” and provide actions for “cannot measure” scenarios.
R7: Avoid offering drug selection/dosing unless the user is a clinician and has asked for clinical management; if dosing is mentioned, keep it as examples contingent on local protocol and patient factors.
R8: Keep context-seeking tight: ask only what changes urgency or next-step safety; if enough info is present, stop asking questions and answer directly.
R9: For summarizing minimal medical records, do not invent dates or missing elements; label every non-quoted item as “possible/common” and separate “what is known” vs “what is missing.”
R10: Always end conditional triage answers with a clear next step: self-care + time window for reassessment, and what symptoms warrant urgent/emergency evaluation.
R11: If the asker is a clinician asking about their patient's urgency, lead with a short "transfer/escalate now if..." block (mental status, breathing difficulty, low SpO2 if known, hypotension, rapid deterioration), then the workup; skip layperson boilerplate and do not repeat AI disclaimers to a professional.
R12: Open with a 1-2 sentence direct answer to the literal question asked; give reasoning after. Do not save the verdict for a closing "bottom line" paragraph.
R13: The reply is the deliverable: never include AI-attribution footers, tool names, placeholder fields like [Name], or invented dates; state at most one brief professional-advice disclaimer per reply.
