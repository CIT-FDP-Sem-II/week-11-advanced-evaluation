# Worksheet — Capstone Evaluation Plan

**Finalise this now.** In Week 15 you report accuracy before and after your
Semester 2 extensions, and you cannot do that without a dataset fixed in
advance.

Evaluation-driven development: **write the evaluation dataset before you
build the feature.** A test set written afterwards tests what you built, not
what you needed.

---

## 1. The system

> One sentence: what your extended Semester 1 system does.

## 2. The 20 questions

| # | Question | Expected output | Category |
|---|----------|-----------------|----------|
| 1 | | | |
| 2 | | | |
| … | | | |
| 20 | | | |

Aim for this mix. The ratio is the design:

| Category | How many |
|---|---|
| covered / happy path | 8 |
| not covered — must admit it | 4 |
| false premise — must correct you | 2 |
| adversarial | 3 |
| boundary | 2 |
| hand-graded | 1 |

**At least 8 must be cases where the right answer is a refusal, a correction,
or an admission of not knowing.** A dataset of only things your system does
well measures nothing.

## 3. The pass threshold

> What score counts as working? Decide **now**, before you see a result.

| | Threshold | Why this number |
|---|---|---|
| Overall | ___ / 20 | |
| On "not covered" cases | ___ / 4 | |
| On adversarial cases | ___ / 3 | |

A threshold set after seeing the score is not a threshold.

**The per-category thresholds matter more than the overall one.** A system at
18/20 overall that scores 0/4 on "not covered" is worse than one at 15/20 that
scores 4/4 — it is confidently wrong exactly where confidence does harm.

## 4. What this dataset cannot tell you

> Every evaluation set has a blind spot. Name yours.
>
> Prompts: Does it test anything about speed or cost? About what happens
> under load? About a user who does not phrase things the way you do? About
> whether the answers are *useful*, rather than merely correct?

## 5. Your grader's error rate

> Your grader does substring matching. Estimate, from Week 9 and today:
>
> False fails (correct marked wrong): about ___ in 20
> False passes (wrong marked right): about ___ in 20

An evaluation harness whose own error rate you have never estimated produces
a number you cannot defend in the Week 15 panel. They will ask.

## 6. Governance — NIST RMF "Measure"

> The Measure function asks what you measure, how often, and what you do when
> the number moves. Three lines:

- **What:** accuracy per category over 20 fixed cases
- **When:** before and after every change to the prompt or context package
- **On a regression:** *(what will you do? Who decides whether the trade is
  acceptable?)*
