---
name: exam-answer-discipline
description: Finish-first discipline for expert exam questions graded on a written answer file.
---

R1: Your FIRST action: write /logs/agent/response.txt with your current best answer in the exact required format (Explanation / Answer / Confidence lines). A best guess now beats a perfect answer never submitted. Every time your reasoning improves, immediately rewrite the file. Never end the episode without this file written.
R2: Use the exact field names and format the task specifies (typically "Explanation:", "Answer:", "Confidence: N%"). The Answer line contains only the answer itself - for multiple choice the single letter, no units unless asked, no sentence, nothing after the Confidence line.
R3: Commit to exactly one answer. Never write "either A or C", "possibly", or two candidate values. If torn, pick the option your reasoning last supported, lower the Confidence number, and stop.
R4: For any multi-step calculation (arithmetic, algebra, combinatorics, unit conversions, stoichiometry, cipher counting), write and run a short Python script and copy its printed result into the file. Never compute multi-step math in your head or in prose.
R5: Never answer "unknown" or "cannot be determined" and never refuse, unless those words are literally among the answer choices. A specific guess with 20% confidence scores; an abstention cannot.
R6: For multiple choice, eliminate options you can prove wrong, then choose among the survivors only.
R7: Budget your turns: by roughly step 25, stop exploring, pick the best-supported answer, write the final file, and finish. Running out of turns with no file is the worst outcome.
