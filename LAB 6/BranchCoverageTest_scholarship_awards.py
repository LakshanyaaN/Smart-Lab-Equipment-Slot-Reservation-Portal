
import pytest
from scholarship_awards import award_amount, is_eligible, application_status


# Award amount branches

def test_unknown_category():
    with pytest.raises(ValueError):
        award_amount("science", 90, "low", False)


def test_negative_marks():
    with pytest.raises(ValueError):
        award_amount("merit", -1, "low", False)


def test_renewal_non_sports():
    assert award_amount("merit", 80, "low", True) == 1000


def test_renewal_sports():
    assert award_amount("sports", 70, "high", True) == 600


def test_non_renewal():
    assert award_amount("merit", 90, "low", False) == 1500


def test_at_cutoff():
    assert award_amount("merit", 75, "low", False) == 0


def test_low_income_high_excess():
    assert award_amount("merit", 100, "low", False) == 4000


def test_high_income_high_excess():
    assert award_amount("merit", 100, "high", False) == 2500


# Eligibility branches

def test_special_quota_with_two_backlogs():
    assert is_eligible(50, 2, True) is True


def test_special_quota_with_three_backlogs():
    assert is_eligible(90, 3, True) is False


def test_normal_quota_low_attendance():
    assert is_eligible(74, 0, False) is False


def test_normal_quota_one_backlog():
    assert is_eligible(75, 1, False) is True


def test_normal_quota_multiple_backlogs():
    assert is_eligible(90, 2, False) is False


# Application status branches

def test_renewal_paper_open():
    assert application_status(40, True, True) == "open"


def test_regular_non_paper_open():
    assert application_status(20, False, False) == "open"


def test_regular_paper_closing():
    assert application_status(15, False, True) == "closing"


def test_regular_paper_closed():
    assert application_status(14, False, True) == "closed"
