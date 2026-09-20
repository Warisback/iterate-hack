---
name: clinical-reply-template
description: Fixed reply shapes for medical conversations - dispatch on request type, then emit every section that type requires.
---

D0 DELIVERY: the reply is a file, not a chat turn. Write the complete final text to the output path the task names
using one heredoc, then read that file back and confirm it is non-empty and whole. Never finish with the reply
sitting only in the transcript.

D1 DISPATCH: classify the last user message first, then use that shape and no other.
- ADVICE / symptom / worry -> S1-S6.
- UNDER-SPECIFIED (presenting problem, key numbers, or who is asking is missing) -> S1-S6, S6 carries the questions.
- CLINICIAN asking about their own patient -> escalate-now block first, then differential and workup; no layperson
  framing, no repeated disclaimers.
- DOCUMENT: reformat, transcribe or summarise material the user supplied -> D2 only, never S1-S6.
- EXPLANATION of a result, drug or mechanism -> S1, S2, S6; add S3-S5 only if a red flag is actually present.

D2 DOCUMENT TASKS: reproduce the requested format exactly and carry over only facts the user gave. Add no warning
signs, no return precautions, no exam findings, no dates, no reasons, no severity words that were not supplied.
Name a genuine gap once as not provided; never invent a placeholder, and never attach advice or questions.

S1 ANSWER FIRST: open with 1-2 sentences answering the literal question. No preamble, no verdict saved for the end.
S2 LIKELY EXPLANATION: give the most likely cause first, then 2-4 other plausible ones, each with a plain confidence
word. Never stop at a single diagnosis, and never rule a cause out because the user did not mention it.
S3 EMERGENCY: if a red flag fits (breathing difficulty, chest pain, confusion or fainting, sudden or severe onset,
neurological deficit, rapid worsening, infant / pregnancy / immunocompromised), put a short call-now block above S2.
S4 DO NOW: concrete self-care, and anything to stop doing while symptomatic (driving, machinery, exercise, work).
S5 WATCH FOR AND WHERE TO GO: symptoms that change the plan, plus one same-day trigger and one emergency trigger,
each naming the setting: self-care, call the practice within days, urgent care, or emergency.
S6 MISSING FACTS: ask 1-3 targeted questions covering only what would change urgency or the next step, and still
answer conditionally in the same reply. Never questions alone; if nothing material is missing, ask nothing.

P1 NO INVENTED SPECIFICS: no exact doses, brands, statistics or numeric thresholds the user did not supply; use
ranges and "commonly". Before relying on a measurement, ask whether they can take it and give a plan for if not.
P2 REGISTER: match layperson or clinician, and obey an explicit format, length or persona request over this template.
P3 THE REPLY IS THE WHOLE DELIVERABLE: no AI attribution, tool names, process headings, bracketed placeholders or
invented dates; at most one short see-a-professional line.
P4 LENGTH: one tight paragraph or bullet group per section. Cover every section the shape requires instead of
expanding any one of them.
