"""The two prompts the regression test compares.

The candidate is a realistic change, not a strawman: someone read the Week 9
results, saw that the model was too terse on multi-part questions, and
loosened the length rule to fix it.

That is a reasonable change. The question Week 11 asks is what else it did.

Keep both prompts here, in version control, with a note on what changed. A
prompt change with no record is the AI equivalent of an undocumented hotfix.
"""

BASELINE = """You are a subject tutor answering a first-year undergraduate's
question about their lecture notes.

Rules:
- Answer only from the notes supplied.
- If the notes do not cover something, say exactly: NOT IN NOTES
- Never invent a lecture or page number.
- If the question contains a statement that the notes contradict, correct it.
- Keep the answer under 120 words."""


# CHANGED from BASELINE:
#   - length limit relaxed from 120 words to "as long as needed"
#   - added encouragement to be thorough
# INTENDED EFFECT: fix the multi-part case (Q20), which was being truncated.
# WATCH FOR: a model told to be thorough has more room to pad, and padding is
#            where invented citations come from.
CANDIDATE = """You are a subject tutor answering a first-year undergraduate's
question about their lecture notes.

Rules:
- Answer only from the notes supplied.
- If the notes do not cover something, say exactly: NOT IN NOTES
- Never invent a lecture or page number.
- If the question contains a statement that the notes contradict, correct it.
- Be thorough and cover every part of the question. Take as long as needed."""


PROMPTS = {"baseline": BASELINE, "candidate": CANDIDATE}


def diff_summary():
    """What changed, in one place, for the write-up."""
    return (
        "baseline  -> candidate\n"
        "  removed: 'Keep the answer under 120 words.'\n"
        "  added:   'Be thorough and cover every part of the question. "
        "Take as long as needed.'\n"
        "  intent:  fix Q20 (multi-part) being truncated\n"
        "  risk:    more room to pad; padding is where invented citations "
        "come from"
    )


if __name__ == "__main__":
    print(diff_summary())
