# A note on the case count

The curriculum says: *"extend the Week 9 evaluation dataset — add 10
adversarial cases and 5 boundary cases"*, and then refers to *"the full
30-case dataset"*.

Those two statements disagree. 20 + 10 + 5 = **35**.

`eval_questions_extended.csv` contains **35 cases**, which is what the
instruction describes. The "30-case" phrasing appears to be a slip.

If your cohort is told to use exactly 30, drop five cases and **say which
five and why** — that is a defensible evaluation decision and makes a better
answer than silently having the wrong number. The five easiest to justify
dropping are the hand-graded ones (Q19, A07, A09, A10 and one other), since
they cannot be scored automatically anyway.

| Group | Count | Source |
|---|------:|--------|
| Original evaluation set | 20 | Week 9 |
| Adversarial | 10 | Added this week |
| Boundary | 5 | Added this week |
| **Total** | **35** | |
