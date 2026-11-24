"""Regression testing for an AI system: did a prompt change make it worse?

    python src/regression.py baseline            # run prompt A, save as baseline
    python src/regression.py candidate           # run prompt B, save as candidate
    python src/regression.py compare             # no API calls - report the delta

    python src/regression.py baseline --limit 10 # cheaper while developing

Each full run is 35 API calls, so a baseline-plus-candidate comparison costs
70. Plan it: run the baseline once, keep it, and only re-run the candidate.

WHY THIS EXISTS
---------------
You change a prompt to fix one case. The fix works. You ship it. Three other
cases that used to pass now fail, and nobody notices because nobody re-ran
them.

That is a regression, and an overall accuracy number hides it: 28/35 before
and 28/35 after looks like no change, while four cases flipped each way. The
only honest report is per-case.

WHAT A DELTA REPORT MUST SHOW
-----------------------------
    FIXED      failed before, passes now   - what you intended
    BROKEN     passed before, fails now    - what you did not intend
    unchanged  the rest

The headline number is BROKEN, not the accuracy.
"""

import sys
import time
from pathlib import Path

import pandas as pd

from gemini_client import GeminiClient, MissingKeyError
from prompts import PROMPTS

ROOT = Path(__file__).parent.parent
DATA = ROOT / "data"
RESULTS = ROOT / "results"
PAUSE_SECONDS = 4

# Cases whose correctness cannot be decided by substring matching. They are
# run and saved, but excluded from the automated score and listed separately
# for a human. Pretending a grader can judge these is how an evaluation
# harness starts lying to you.
HAND_GRADED = {"Q19", "A07", "A09", "A10"}


def grade(response, must_contain, must_not_contain):
    """Case-insensitive substring matching. Returns (passed, reason)."""
    text = response.lower()
    reasons = []

    for phrase in [p for p in str(must_contain).split("|") if p.strip()]:
        if phrase.strip().lower() not in text:
            reasons.append(f"missing '{phrase.strip()}'")

    for phrase in [p for p in str(must_not_contain).split("|") if p.strip()]:
        if phrase.strip().lower() in text:
            reasons.append(f"forbidden '{phrase.strip()}'")

    return (not reasons), "; ".join(reasons)


def run(label, limit=None):
    """Run the whole dataset against one prompt and save the results."""
    if label not in PROMPTS:
        print(f"Unknown prompt {label!r}. Choose from: {', '.join(PROMPTS)}")
        return 1

    questions = pd.read_csv(DATA / "eval_questions_extended.csv").fillna("")
    notes = (DATA / "notes.txt").read_text(encoding="utf-8")
    if limit:
        questions = questions.head(limit)

    try:
        client = GeminiClient()
    except MissingKeyError as exc:
        print(f"STOPPED: {exc}")
        return 1

    RESULTS.mkdir(exist_ok=True)
    system = PROMPTS[label]
    print(f"prompt: {label}\n{len(questions)} cases = {len(questions)} API calls\n")

    rows = []
    for _, question in questions.iterrows():
        message = f"{question['question']}\n\nNOTES:\n{notes}"
        try:
            response = client.ask(message, system=system)
            error = ""
        except Exception as exc:
            response, error = "", f"{type(exc).__name__}: {exc}"

        if error:
            passed, reason = False, error
        else:
            passed, reason = grade(
                response, question["must_contain"], question["must_not_contain"]
            )

        rows.append({
            "id": question["id"],
            "category": question["category"],
            "question": question["question"],
            "response": response,
            "passed": passed,
            "reason": reason,
            "hand_graded": question["id"] in HAND_GRADED,
        })
        print(f"  {question['id']:<5}{'pass' if passed else 'FAIL':<6}{reason}")
        time.sleep(PAUSE_SECONDS)

    frame = pd.DataFrame(rows)
    frame.to_csv(RESULTS / f"{label}.csv", index=False)
    print(f"\nsaved to results/{label}.csv")
    print(report_accuracy(frame, label))
    return 0


def report_accuracy(frame, label):
    """Accuracy per category, excluding the hand-graded cases."""
    scored = frame[~frame["hand_graded"]]
    lines = [f"\nACCURACY ({label}) - {len(scored)} auto-scored cases", "=" * 48]
    grouped = scored.groupby("category")["passed"].agg(["sum", "count"])
    for category, row in grouped.iterrows():
        lines.append(f"  {category:<22}{int(row['sum'])}/{int(row['count'])}")
    total, n = int(scored["passed"].sum()), len(scored)
    lines.append(f"  {'OVERALL':<22}{total}/{n}  ({100 * total / n:.0f}%)")
    lines.append(
        f"  {len(frame) - n} case(s) hand-graded, excluded from this score: "
        f"{', '.join(sorted(HAND_GRADED & set(frame['id'])))}"
    )
    return "\n".join(lines)


def compare():
    """The delta report. No API calls - reads the two saved runs."""
    paths = {label: RESULTS / f"{label}.csv" for label in ("baseline", "candidate")}
    for label, path in paths.items():
        if not path.exists():
            print(f"Cannot find {path}. Run: python src/regression.py {label}")
            return 1

    before = pd.read_csv(paths["baseline"]).set_index("id")
    after = pd.read_csv(paths["candidate"]).set_index("id")
    shared = before.index.intersection(after.index)
    before, after = before.loc[shared], after.loc[shared]

    fixed = shared[(~before["passed"]) & (after["passed"])]
    broken = shared[(before["passed"]) & (~after["passed"])]

    before_score = int(before["passed"].sum())
    after_score = int(after["passed"].sum())

    print("REGRESSION REPORT")
    print("=" * 56)
    print(f"baseline   {before_score}/{len(shared)}")
    print(f"candidate  {after_score}/{len(shared)}")
    print(f"delta      {after_score - before_score:+d}\n")

    print(f"FIXED ({len(fixed)}) - failed before, passes now")
    for case in fixed:
        print(f"  + {case}  [{after.loc[case, 'category']}]  "
              f"was: {before.loc[case, 'reason']}")

    print(f"\nBROKEN ({len(broken)}) - passed before, FAILS NOW")
    for case in broken:
        print(f"  - {case}  [{after.loc[case, 'category']}]  "
              f"now: {after.loc[case, 'reason']}")

    print("\n" + "=" * 56)
    if len(broken) == 0:
        print("No regressions. The change is safe to keep.")
    else:
        print(f"{len(broken)} REGRESSION(S). The delta of "
              f"{after_score - before_score:+d} hides this.")
        print("Decide per case whether the trade is worth it, and write it down.")

    if before_score == after_score and (len(fixed) or len(broken)):
        print("\nNote: the totals are identical and "
              f"{len(fixed) + len(broken)} cases still changed. This is exactly "
              "why an overall accuracy number is not a regression test.")

    pd.DataFrame({
        "id": list(fixed) + list(broken),
        "change": ["fixed"] * len(fixed) + ["broken"] * len(broken),
    }).to_csv(RESULTS / "delta.csv", index=False)
    print(f"\nsaved to results/delta.csv")
    return 0


def main(argv):
    if len(argv) < 2:
        print(__doc__.split("WHY THIS EXISTS")[0].strip())
        return 2

    command = argv[1]
    limit = None
    if "--limit" in argv:
        limit = int(argv[argv.index("--limit") + 1])

    if command == "compare":
        return compare()
    return run(command, limit)


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
