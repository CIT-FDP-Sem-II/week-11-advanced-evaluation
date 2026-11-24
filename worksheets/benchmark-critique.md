# Worksheet — Benchmark Critique

**200 words. 20 minutes.** Pick one published AI benchmark and write what it
measures and what it misses.

## Pick one

| Benchmark | What it claims to measure |
|---|---|
| **MMLU** | General knowledge across 57 subjects, multiple choice |
| **HumanEval** | Code generation from docstrings, checked by unit tests |
| **GSM8K** | Grade-school maths word problems |
| **HellaSwag** | Commonsense sentence completion |
| **TruthfulQA** | Whether a model repeats common misconceptions |
| **SWE-bench** | Resolving real GitHub issues in real repositories |

## The five questions

Answer these in notes, then write the 200 words.

**1. What exactly is the task?** Not the name — the actual thing the model is
asked to do, and how a response is scored.

**2. What does a high score let you conclude?** Be strict. "It is good at
maths" is almost never what a maths benchmark supports.

**3. What does it not measure that a user would care about?**

**4. Could a model score well without the underlying ability?** The usual
routes: the test set is in the training data; the format rewards a guessing
strategy; multiple choice lets elimination substitute for knowledge.

**5. What would it take to game it deliberately?** If the answer is cheap,
the benchmark stops measuring ability as soon as it becomes important enough
to target.

## The 200 words

> Structure: what it measures (50) · what it misses (100) · what you would
> conclude from a high score (50).

---

*(your 200 words)*

---

## Worked fragment — for shape, not to copy

> HumanEval scores a model on 164 Python problems by generating a function
> body from a docstring and running hidden unit tests. Pass@1 is the fraction
> solved on the first attempt.
>
> What it misses is most of programming. The problems are self-contained,
> under about twenty lines, have no dependencies, no existing codebase to fit
> into, and a complete specification in the docstring — a situation that
> almost never occurs in the work the score is used to predict. Nothing is
> measured about reading unfamiliar code, choosing between two defensible
> designs, or noticing that the request is wrong. The tests are also the
> entire definition of correct, so a solution that passes them while being
> unmaintainable scores identically to a good one.
>
> It is also six years old and public, which makes contamination hard to rule
> out: a high score may reflect memorisation rather than synthesis, and no
> part of the published number distinguishes the two.
>
> A high score supports one claim: the model can usually turn a complete,
> small, self-contained specification into working Python. That is worth
> knowing. It is not evidence that it can work in your codebase.

## The connection to your own work

The last paragraph is what you did in Week 9 when you reported accuracy **by
category** instead of as one number.

> Which of the five criticisms above applies to **your own** evaluation
> dataset?

Be specific. "Mine is small too" is a start; "my covered questions use the
same wording as the notes, so a model could pass by echoing" is a finding.
