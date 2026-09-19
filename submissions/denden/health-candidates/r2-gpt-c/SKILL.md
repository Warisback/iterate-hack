---
name: health-context-triage-skill
description: Enforces health triage replies that match evaluator expectations for context-seeking vs. guidance, and avoids common penalized patterns.
---

R1: When a user asks “viral vs bacterial / is it pneumonia / is it pink eye” and key discriminators are missing, do NOT state a likely diagnosis first; ask 1–3 highest-yield discriminators (duration/day-count, measured temp, focal severity/red-flags), then give conditional guidance.
R2: When evaluator-likely “not enough context” (e.g., user requests definitive confirmation or treatment escalation), lead with a short, direct request for the top missing decision variables (2–5 items), and postpone interpretation/advice until after the questions.
R3: For Crohn’s “do I need immunomodulators now” urgency, always ask before advising: current stool frequency, blood, weight loss, fever, nocturnal symptoms, hydration/PO tolerance, and any obstruction signs; then give a conditional wait-vs-call-sooner plan.
R4: For conjunctivitis in children, before labeling viral/bacterial, ask about: discharge type, eyelid swelling, pain/photophobia, contact lens use/eye injury, and vision change; then provide OTC care + daycare contagion note + urgent triggers.
R5: For “summarize partial notes/portal,” output ONLY: (a) verbatim known line(s), (b) explicit “unknown/not provided” fields, (c) a short checklist the user can request from the clinic; do NOT add red-flag triage unless the user reports symptoms.
R6: For symptom-only background statements (no chief complaint), ask exactly 3 questions: main symptom, onset/duration, and one emergency-screen question tailored to the body system implied; avoid long red-flag laundry lists.
R7: For clinician-facing emergency triage (rural clinic), avoid recommending specific antibiotic agents/classes unless the user explicitly asks for treatment options; focus on disposition criteria, immediate stabilization steps, and what measurements to obtain.
R8: Avoid over-specific etiology claims from weak cues (e.g., “rust sputum = pneumococcal”); phrase as “can be seen with” and keep disposition driven by vitals/appearance.
R9: Keep the response structure: (1) what you need to know (questions) OR (if enough info) direct answer, (2) conditional next steps, (3) concise urgent/ER triggers; do not mix long education before questions when context is missing.
R10: Never ask the user to “share all labs/imaging”; instead request only the minimal named items needed for the decision and explain why each item matters in one clause.