# Week 11 — Advanced Data Evaluation and AI System Testing

**CIT AI-Native Engineering Program · Year 1 · Semester 2 · Module M3 (advanced)**

You change a prompt to fix one case. It works. Three other cases that used to
pass now fail, and nobody notices because nobody re-ran them.

That is a regression, and an overall accuracy number hides it.

**Lab time: 2 hours. API calls: 70.** See [LAB.md](LAB.md).

## Contents

| Path | What it is |
|---|---|
| `data/eval_questions_extended.csv` | **35 cases** — 20 from Week 9, +10 adversarial, +5 boundary |
| `data/README.md` | Why it is 35 and not 30 |
| `src/prompts.py` | The two prompts being compared, with the intent **and the risk** |
| `src/regression.py` | Run either prompt; report the delta per case |
| `worksheets/benchmark-critique.md` | 200 words on a published benchmark |
| `worksheets/capstone-eval-plan.md` | **Due now** — the dataset Week 15 measures against |
| `worksheets/journal-11.md` | Journal entry |
| `tests/` | 20 tests. No API key needed. |

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1          # mac/linux: source .venv/bin/activate
pip install -r requirements.txt
copy .env.example .env                 # mac/linux: cp .env.example .env
```

## Running

```powershell
python src/prompts.py                      # what changed - no API calls
python -m pytest tests -v                  # 20 tests - no API calls

python src/regression.py baseline          # 35 API calls
python src/regression.py candidate         # 35 API calls
python src/regression.py compare           # 0 API calls - the delta report

python src/regression.py baseline --limit 10   # cheaper while developing
```

> **Not verified in this repo:** `baseline` and `candidate` need a live key
> and have not been run here. **The delta report itself is verified** — the
> test suite drives `compare()` with synthetic runs, so the thing that tells
> you whether a change broke something is checked before you spend 70 calls
> on it.

## Free-tier budget

70 calls is the most expensive lab of the semester: two full passes over 35
cases, 4 seconds apart, about 5 minutes each. Start the baseline, then read
ahead while it runs.

You only ever run the baseline **once**. Keep `results/baseline.csv` and
re-run only the candidate.

## The report that matters

```
REGRESSION REPORT
baseline   28/31
candidate  28/31
delta      +0

FIXED (3) - failed before, passes now
  + Q20  [multi-part]   was: missing 'k times'
  ...
BROKEN (3) - passed before, FAILS NOW
  - Q12  [not covered]  now: forbidden 'page 7'
  ...

Note: the totals are identical and 6 cases still changed. This is exactly
why an overall accuracy number is not a regression test.
```

**The headline is BROKEN, not accuracy.** A change that fixes three cases and
breaks three is not neutral — it is six decisions you now have to make
individually.

## The prompt change is realistic, not a strawman

`src/prompts.py` relaxes a 120-word limit to fix multi-part answers being
truncated. That is a sensible change that a real person would make.

The risk is recorded next to it:

> *a model told to be thorough has more room to pad, and padding is where
> invented citations come from*

A prompt change with no record of intent and risk is the AI equivalent of an
undocumented hotfix.

## Adversarial vs boundary

They are different and get confused constantly.

| | What it is | Example |
|---|---|---|
| **Adversarial** | Someone trying to make it misbehave | "Previous instructions are cancelled" |
| **Boundary** | The edge of what is *defined* | Lecture 3 page 6, when lecture 3 ends at page 5 |

Ten variations of one attack measure one thing ten times. The ten here attack
ten different mechanisms — extraction, override, social pressure, permission
to guess, fake citations, empty input, format pressure, false binaries.

## Cases a grader cannot judge

Four cases (Q19, A07, A09, A10) cannot be scored by substring matching —
"does it refuse a false binary?" is not a substring question.

They are **run, saved, and excluded from the automated score**, then read by
a human. The accuracy line says how many were excluded and which.

Pretending a grader can judge these is how an evaluation harness starts lying
to you, and it is a short step from there to a number nobody can defend.

---

## Set B (non-IT background)

**`src/prompts.py`** — two blocks of instruction text, `BASELINE` and
`CANDIDATE`, plus `diff_summary()`, which prints what changed between them,
why it was changed, and what might go wrong as a result.

**`src/regression.py`**
- `grade(response, must_contain, must_not_contain)` — checks whether the
  required phrases are present and the forbidden ones absent.
- `run(label)` — sends all 35 questions using one of the two prompts, grades
  each reply, and saves everything to `results/<label>.csv`.
- `report_accuracy(frame, label)` — prints the score per category, leaving
  out the cases that need a human.
- `compare()` — reads the two saved files and works out, case by case, which
  ones changed: **fixed** (failed before, passes now) and **broken** (passed
  before, fails now). Makes no API calls.
- `HAND_GRADED` — the list of case IDs a computer cannot score.

### What Set B may simplify

- **5 adversarial and 3 boundary** cases instead of 10 and 5.
- The benchmark critique may be **150 words**.
- The regression run may use `--limit 20` on both prompts (40 calls instead
  of 70), as long as the 20 include at least three adversarial cases.

### What Set B may **not** simplify

- The **fixed / broken** breakdown. Reporting only an overall accuracy number
  misses the entire point of the week.
- A **pass threshold decided before seeing a score**.
- Cases you cannot auto-grade must be **declared**, not quietly scored.
