"Pure functions that turn fund records from GET /funds into chart and table data. No Streamlit, no network."

import pandas as pd


def sector_exposure(funds: list[dict]) -> pd.DataFrame:
    "Sector (rows) by fund name (columns), summing holding weights. Top positions only, not the whole fund."
    return pd.DataFrame({
        f["name"]: pd.Series(
            [h["weight_pct"] for h in f["holdings"]],
            index=[h["sector"] for h in f["holdings"]],
        ).groupby(level=0).sum()
        for f in funds
    }).fillna(0)


def nav_frame(funds: list[dict]) -> pd.DataFrame:
    "Quarter (rows, Q1 oldest) by fund name (columns), for a line chart."
    return pd.DataFrame({
        f["name"]: pd.Series({n["quarter"]: n["nav"] for n in f["NAV_per_share"]})
        for f in funds
    })


def fund_highlights(funds: list[dict]) -> dict[str, list[str]]:
    "Names of the cheapest and the highest-risk fund. A tie returns every tied fund."
    fee = min(f["ongoing_charge_pct"] for f in funds)
    risk = max(f["risk_rating"] for f in funds)
    return {
        "cheapest": [f["name"] for f in funds if f["ongoing_charge_pct"] == fee],
        "highest_risk": [f["name"] for f in funds if f["risk_rating"] == risk],
    }
