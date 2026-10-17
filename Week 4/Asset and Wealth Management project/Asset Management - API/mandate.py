"Deterministic mandate rules. Read records only, never documents. Pure functions: no network, no model, no FastAPI."

from Data.records import FUNDS

ESG_ORDER = {"A": 4, "B": 3, "C": 2, "D": 1}  # "unrated" is absent on purpose: it ranks 0 and fails any minimum


def check_fund(client: dict, fund: dict) -> list[dict]:
    """Apply the five mandate rules and return the breaches (empty list means none).

    A value equal to a limit is compliant, and a rule that is None on the client is skipped.
    Holdings are top positions only, so no breach means none among reported holdings, not zero exposure."""
    breaches = []

    excluded = client["excluded_sectors"] or []
    found: dict[str, float] = {}
    for h in fund["holdings"]:
        if h["sector"] in excluded:
            found[h["sector"]] = round(found.get(h["sector"], 0) + h["weight_pct"], 4)
    if found:
        breaches.append({"rule": "excluded_sector", "actual": found, "limit": excluded,
                         "detail": "Holds excluded sectors: " + ", ".join(f"{s} {w}%" for s, w in found.items())})

    if client["risk_tolerance"] is not None and fund["risk_rating"] > client["risk_tolerance"]:
        breaches.append({"rule": "risk", "actual": fund["risk_rating"], "limit": client["risk_tolerance"],
                         "detail": f"Risk rating {fund['risk_rating']} is above the client's tolerance of {client['risk_tolerance']}"})

    limit = client["max_single_holding_pct"]
    if limit is not None:
        biggest = max((h["weight_pct"] for h in fund["holdings"]), default=0)
        if biggest > limit:
            breaches.append({"rule": "concentration", "actual": biggest, "limit": limit,
                             "detail": f"Largest holding is {biggest}%, above the {limit}% limit"})

    if client["min_esg_rating"] is not None and ESG_ORDER.get(fund["esg_rating"], 0) < ESG_ORDER[client["min_esg_rating"]]:
        breaches.append({"rule": "esg", "actual": fund["esg_rating"], "limit": client["min_esg_rating"],
                         "detail": f"ESG rating {fund['esg_rating']} is below the client's minimum of {client['min_esg_rating']}"})

    if client["max_ongoing_charge_pct"] is not None and fund["ongoing_charge_pct"] > client["max_ongoing_charge_pct"]:
        breaches.append({"rule": "fee", "actual": fund["ongoing_charge_pct"], "limit": client["max_ongoing_charge_pct"],
                         "detail": f"Ongoing charge {fund['ongoing_charge_pct']}% is above the {client['max_ongoing_charge_pct']}% ceiling"})

    return breaches


def look_through_exposure(portfolio: dict, sector: str) -> float:
    "Effective portfolio exposure to a sector: sum of position weight x holding weight / 100. Cash adds nothing."
    return sum(
        p["weight_pct"] * h["weight_pct"] / 100
        for p in portfolio["positions"]
        for h in FUNDS[p["fund_id"]]["holdings"]
        if h["sector"] == sector
    )
