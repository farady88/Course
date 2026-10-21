import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from helpers import fund_highlights, nav_frame, sector_exposure

A = {
    "name": "Fund A", "ongoing_charge_pct": 0.5, "risk_rating": 5,
    "holdings": [{"name": "x", "sector": "technology", "weight_pct": 6.0},
                 {"name": "y", "sector": "technology", "weight_pct": 4.0},
                 {"name": "z", "sector": "financials", "weight_pct": 5.0}],
    "NAV_per_share": [{"quarter": q, "nav": n} for q, n in zip(["Q1", "Q2", "Q3", "Q4"], [1.0, 1.1, 1.2, 1.3])],
}
B = {
    "name": "Fund B", "ongoing_charge_pct": 0.5, "risk_rating": 3,
    "holdings": [{"name": "w", "sector": "government", "weight_pct": 12.0}],
    "NAV_per_share": [{"quarter": q, "nav": 2.0} for q in ["Q1", "Q2", "Q3", "Q4"]],
}


def test_sector_exposure_sums_within_a_fund_and_zero_fills_the_other():
    df = sector_exposure([A, B])
    assert df.loc["technology", "Fund A"] == 10.0
    assert df.loc["financials", "Fund A"] == 5.0
    assert df.loc["government", "Fund A"] == 0 and df.loc["technology", "Fund B"] == 0


def test_nav_frame_is_quarters_by_fund():
    df = nav_frame([A, B])
    assert list(df.index) == ["Q1", "Q2", "Q3", "Q4"] and list(df.columns) == ["Fund A", "Fund B"]
    assert df.loc["Q4", "Fund A"] == 1.3


def test_highlights_return_every_fund_on_a_tie():
    assert fund_highlights([A, B]) == {"cheapest": ["Fund A", "Fund B"], "highest_risk": ["Fund A"]}
