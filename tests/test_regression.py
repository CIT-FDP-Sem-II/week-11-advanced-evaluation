"""Tests for the regression harness. No API calls.

The delta report is verified against synthetic runs, so the thing that will
tell you whether a prompt change broke something is itself checked before you
trust it with 70 real calls.
"""

import sys
from pathlib import Path

import pandas as pd
import pytest

ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT / "src"))

import regression
from prompts import BASELINE, CANDIDATE, PROMPTS, diff_summary
from regression import HAND_GRADED, grade, report_accuracy

CASES = pd.read_csv(ROOT / "data" / "eval_questions_extended.csv").fillna("")
NOTES = (ROOT / "data" / "notes.txt").read_text(encoding="utf-8")


# --- the dataset ---------------------------------------------------------

def test_the_set_is_twenty_plus_ten_plus_five():
    counts = CASES["category"].value_counts()
    assert counts["adversarial"] == 10
    assert counts["boundary"] == 5
    assert len(CASES) == 35, "20 original + 10 adversarial + 5 boundary"


def test_case_ids_are_unique():
    assert CASES["id"].is_unique


def test_every_case_says_why_it_exists():
    assert (CASES["why"].str.len() > 10).all()


def test_adversarial_cases_attack_different_things():
    """Ten variations of one attack would measure one thing ten times."""
    reasons = CASES[CASES["category"] == "adversarial"]["why"].str.split(".").str[0]
    assert reasons.nunique() == 10


def test_boundary_cases_sit_on_the_edges_of_the_citable_range():
    boundary = CASES[CASES["category"] == "boundary"]
    questions = " ".join(boundary["question"])
    assert "lecture 3, page 4" in questions.lower(), "lower edge missing"
    assert "lecture 6, page 3" in questions.lower(), "upper edge missing"
    assert "lecture 3, page 6" in questions.lower(), "off-by-one case missing"


def test_the_off_by_one_boundary_case_is_genuinely_undefined():
    """B03 only works if lecture 3 really stops before page 6."""
    assert "Lecture 3, page 6" not in NOTES


def test_hand_graded_cases_are_declared_and_real():
    """A case a substring grader cannot judge must be excluded, not faked."""
    assert HAND_GRADED <= set(CASES["id"]), "a hand-graded id is not in the dataset"
    assert len(HAND_GRADED) >= 3


# --- the prompts ---------------------------------------------------------

def test_the_candidate_differs_from_the_baseline():
    assert BASELINE != CANDIDATE
    assert set(PROMPTS) == {"baseline", "candidate"}


def test_the_change_is_the_length_rule():
    assert "under 120 words" in BASELINE
    assert "under 120 words" not in CANDIDATE
    assert "Take as long as needed" in CANDIDATE


def test_the_constraints_that_matter_survive_the_change():
    """Whatever else the candidate does, it must not drop the two rules the
    adversarial cases test."""
    for rule in ["NOT IN NOTES", "Never invent a lecture or page number"]:
        assert rule in BASELINE and rule in CANDIDATE


def test_the_diff_is_documented():
    summary = diff_summary()
    assert "intent" in summary and "risk" in summary


# --- the grader ----------------------------------------------------------

def test_grader_passes_a_correct_answer():
    assert grade("Precision is TP / (TP + FP).", "TP|FP", "")[0]


def test_grader_catches_a_forbidden_phrase():
    passed, reason = grade("See lecture 9, page 3.", "NOT IN NOTES", "lecture 9")
    assert not passed
    assert "forbidden" in reason


def test_grader_reports_every_failure_not_only_the_first():
    _, reason = grade("Nothing useful.", "TP|FP", "")
    assert "TP" in reason and "FP" in reason


# --- the delta report ----------------------------------------------------

def synthetic(tmp_path, before_passes, after_passes):
    """Write two fake runs so compare() can be tested without any API calls."""
    ids = ["Q01", "Q02", "Q03", "Q04"]
    for label, passes in [("baseline", before_passes), ("candidate", after_passes)]:
        pd.DataFrame({
            "id": ids,
            "category": ["covered"] * 4,
            "question": ["q"] * 4,
            "response": ["r"] * 4,
            "passed": passes,
            "reason": ["" if p else "missing 'x'" for p in passes],
            "hand_graded": [False] * 4,
        }).to_csv(tmp_path / f"{label}.csv", index=False)


@pytest.fixture
def results_dir(tmp_path, monkeypatch):
    monkeypatch.setattr(regression, "RESULTS", tmp_path)
    return tmp_path


def test_compare_reports_a_clean_improvement(results_dir, capsys):
    synthetic(results_dir, [False, True, True, True], [True, True, True, True])
    assert regression.compare() == 0
    out = capsys.readouterr().out
    assert "FIXED (1)" in out
    assert "BROKEN (0)" in out
    assert "No regressions" in out


def test_compare_names_every_regression(results_dir, capsys):
    synthetic(results_dir, [True, True, True, False], [False, True, True, True])
    regression.compare()
    out = capsys.readouterr().out
    assert "BROKEN (1)" in out
    assert "- Q01" in out
    assert "1 REGRESSION(S)" in out


def test_an_unchanged_total_still_reports_the_churn(results_dir, capsys):
    """The headline case for this week: 3/4 before, 3/4 after, two cases
    flipped. An accuracy number alone would call this 'no change'."""
    synthetic(results_dir, [True, True, True, False], [False, True, True, True])
    regression.compare()
    out = capsys.readouterr().out
    assert "delta      +0" in out
    assert "why an overall accuracy number is not a regression test" in out


def test_compare_refuses_politely_when_a_run_is_missing(results_dir, capsys):
    assert regression.compare() == 1
    assert "Run: python src/regression.py baseline" in capsys.readouterr().out


def test_compare_writes_a_delta_file(results_dir):
    synthetic(results_dir, [False, True, True, True], [True, True, True, True])
    regression.compare()
    delta = pd.read_csv(results_dir / "delta.csv")
    assert list(delta["change"]) == ["fixed"]


# --- accuracy reporting --------------------------------------------------

def test_hand_graded_cases_are_excluded_from_the_score():
    frame = pd.DataFrame({
        "id": ["Q01", "A07"],
        "category": ["covered", "adversarial"],
        "passed": [True, False],
        "hand_graded": [False, True],
    })
    report = report_accuracy(frame, "test")
    assert "1/1" in report, "the hand-graded failure must not count against the score"
    assert "hand-graded, excluded" in report
