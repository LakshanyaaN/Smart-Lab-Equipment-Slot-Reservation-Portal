
import pytest
from scholarship_awards import award_amount, is_eligible, application_status


# Award amount tests

def test_unknown_category():
    with pytest.raises(ValueError):
        award_amount("science", 90, "low", False)


def test_invalid_marks():
    with pytest.raises(ValueError):
        award_amount("merit", -5, "low", False)


def test_marks_at_cutoff():
    assert award_amount("merit", 75, "low", False) == 0


def test_renewal_merit():
    assert award_amount("merit", 80, "low", True) == 1000


def test_renewal_sports():
    assert award_amount("sports", 70, "high", True) == 600


def test_high_marks_low_income():
    assert award_amount("merit", 100, "low", False) == 4000


def test_high_marks_high_income():
    assert award_amount("merit", 100, "high", False) == 2500


# Eligibility tests

def test_special_quota_eligible():
    assert is_eligible(60, 2, True) is True


def test_special_quota_ineligible():
    assert is_eligible(90, 3, True) is False


def test_low_attendance():
    assert is_eligible(70, 0, False) is False


def test_eligible_with_one_backlog():
    assert is_eligible(80, 1, False) is True


def test_ineligible_with_multiple_backlogs():
    assert is_eligible(90, 2, False) is False


# Application status tests

def test_renewal_paper_open():
    assert application_status(40, True, True) == "open"


def test_regular_application_closing():
    assert application_status(5, False, False) == "closing"


def test_regular_paper_closed():
    assert application_status(14, False, True) == "closed"
