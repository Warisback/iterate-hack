---
name: exam-answer-discipline
description: Answer-format and reasoning discipline for expert exam questions graded on the final answer.
---

R1: End every response with exactly this block and nothing after it:
Explanation: {1-3 sentences}
Exact Answer: {the answer only — for multiple choice, the single letter; no units unless asked; no sentence}
Confidence: {N}%
R2: Commit to exactly one answer. Never write "either A or C", "possibly", or two candidate values in the final block. If torn, pick the option your reasoning last supported and stop.
R3: For any multi-step calculation (arithmetic, algebra, combinatorics, unit conversion, stoichiometry), write and run a Python script in the sandbox and copy its printed result into Exact Answer. Never compute multi-step math in prose.
R4: Never answer "unknown" or "cannot be determined" and never refuse, unless those words are literally among the answer choices. Always give your best specific answer, with a low Confidence number if unsure.
R5: For multiple choice, first eliminate the options you can prove wrong, then choose among the survivors only.
R6: Answer in the exact form the question requests (significant figures, notation, name vs formula). Re-read the final sentence of the question before writing Exact Answer.
