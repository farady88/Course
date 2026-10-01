"""In-memory record store and seed data. All data is synthetic.

Each store is a dict keyed by record id. Every record also carries its own "id".
"""

from datetime import date

# Fixed list of sectors a holding may belong to (guide section 4.1).
SECTORS = [
    "technology",
    "financials",
    "healthcare",
    "consumer_staples",
    "consumer_discretionary",
    "industrials",
    "materials",
    "utilities",
    "real_estate",
    "telecommunications",
    "government",
    "fossil_fuels",
    "tobacco",
    "weapons",
    "gambling",
]

# ---------------------------------------------------------------------------
# Funds
# strategy: equity | fixed_income | multi_asset | emerging_markets | sustainable
# esg_rating: A | B | C | D | unrated
# Holdings list the top positions only, so weights sum to at most 100.
# ---------------------------------------------------------------------------
FUNDS = {
    1: {
        "id": 1,
        "name": "Meridian Global Equity Growth",
        "strategy": "equity",
        "region": "Global",
        "ongoing_charge_pct": 0.85,
        "risk_rating": 5,
        "esg_rating": "B",
        "inception_date": date(2014, 3, 17),
        "Percentage_of_fund_represented": 47.1,
        "NAV_per_share": [
            {"quarter": "Q1", "nav": 3.82},
            {"quarter": "Q2", "nav": 3.95},
            {"quarter": "Q3", "nav": 4.08},
            {"quarter": "Q4", "nav": 4.21},
        ],
        "holdings": [
            {"name": "Northbridge Software", "sector": "technology", "weight_pct": 7.5},
            {"name": "Aurelia Semiconductors", "sector": "technology", "weight_pct": 6.8},
            {"name": "Calder Bank", "sector": "financials", "weight_pct": 5.2},
            {"name": "Helix Biopharma", "sector": "healthcare", "weight_pct": 5.0},
            {"name": "Vantor Cloud", "sector": "technology", "weight_pct": 4.6},
            {"name": "Pemberton Insurance", "sector": "financials", "weight_pct": 4.1},
            {"name": "Orrin Consumer Brands", "sector": "consumer_discretionary", "weight_pct": 3.9},
            {"name": "Stanmore Industrial", "sector": "industrials", "weight_pct": 3.6},
            {"name": "Lumen Health Devices", "sector": "healthcare", "weight_pct": 3.4},
            {"name": "Tessaly Retail", "sector": "consumer_discretionary", "weight_pct": 3.0},
        ],
    },
    # Edge case: holds 3% tobacco.
    2: {
        "id": 2,
        "name": "Meridian Emerging Markets Equity",
        "strategy": "emerging_markets",
        "region": "Emerging Markets",
        "ongoing_charge_pct": 1.45,
        "risk_rating": 6,
        "esg_rating": "C",
        "inception_date": date(2011, 9, 5),
        "Percentage_of_fund_represented": 46.2,
        "NAV_per_share": [
            {"quarter": "Q1", "nav": 2.46},
            {"quarter": "Q2", "nav": 2.38},
            {"quarter": "Q3", "nav": 2.51},
            {"quarter": "Q4", "nav": 2.44},
        ],
        "holdings": [
            {"name": "Jade Dragon Electronics", "sector": "technology", "weight_pct": 8.2},
            {"name": "Bharat Private Bank", "sector": "financials", "weight_pct": 6.5},
            {"name": "Costa Verde Mining", "sector": "materials", "weight_pct": 5.4},
            {"name": "Pampas Energy", "sector": "fossil_fuels", "weight_pct": 4.8},
            {"name": "Sunrise Telecom", "sector": "telecommunications", "weight_pct": 4.4},
            {"name": "Ankara Retail Group", "sector": "consumer_discretionary", "weight_pct": 4.0},
            {"name": "Lagos Cement", "sector": "materials", "weight_pct": 3.6},
            {"name": "Andes Utilities", "sector": "utilities", "weight_pct": 3.2},
            {"name": "Mekong Consumer Staples", "sector": "consumer_staples", "weight_pct": 3.1},
            {"name": "Kestrel Tobacco Holdings", "sector": "tobacco", "weight_pct": 3.0},
        ],
    },
    # Edge case: clean on every rule for a typical ethical mandate.
    3: {
        "id": 3,
        "name": "Meridian Sustainable Global Equity",
        "strategy": "sustainable",
        "region": "Global",
        "ongoing_charge_pct": 0.70,
        "risk_rating": 4,
        "esg_rating": "A",
        "inception_date": date(2018, 6, 11),
        "Percentage_of_fund_represented": 41.7,
        "NAV_per_share": [
            {"quarter": "Q1", "nav": 5.10},
            {"quarter": "Q2", "nav": 5.18},
            {"quarter": "Q3", "nav": 5.27},
            {"quarter": "Q4", "nav": 5.39},
        ],
        "holdings": [
            {"name": "Solvane Renewables", "sector": "utilities", "weight_pct": 5.5},
            {"name": "Nordic Wind Power", "sector": "utilities", "weight_pct": 5.0},
            {"name": "Ecotrans Rail", "sector": "industrials", "weight_pct": 4.8},
            {"name": "Bright Grid Software", "sector": "technology", "weight_pct": 4.6},
            {"name": "Clearwater Utilities", "sector": "utilities", "weight_pct": 4.2},
            {"name": "Verdant Health", "sector": "healthcare", "weight_pct": 4.0},
            {"name": "Harbor Green Bank", "sector": "financials", "weight_pct": 3.8},
            {"name": "Circula Packaging", "sector": "materials", "weight_pct": 3.5},
            {"name": "Helio Solar", "sector": "technology", "weight_pct": 3.3},
            {"name": "Orbis Medical", "sector": "healthcare", "weight_pct": 3.0},
        ],
    },
    # Edge case: a 12% single holding breaches tight concentration limits.
    4: {
        "id": 4,
        "name": "Meridian Global Government and Corporate Bond",
        "strategy": "fixed_income",
        "region": "Global",
        "ongoing_charge_pct": 0.45,
        "risk_rating": 3,
        "esg_rating": "B",
        "inception_date": date(2009, 1, 19),
        "Percentage_of_fund_represented": 38.0,
        "NAV_per_share": [
            {"quarter": "Q1", "nav": 10.42},
            {"quarter": "Q2", "nav": 10.45},
            {"quarter": "Q3", "nav": 10.41},
            {"quarter": "Q4", "nav": 10.47},
        ],
        "holdings": [
            {"name": "Government of Alderland", "sector": "government", "weight_pct": 12.0},
            {"name": "Republic of Norvale", "sector": "government", "weight_pct": 9.5},
            {"name": "Calder Bank", "sector": "financials", "weight_pct": 4.0},
            {"name": "Vantor Corp", "sector": "technology", "weight_pct": 3.5},
            {"name": "Stanmore Industrial", "sector": "industrials", "weight_pct": 3.2},
            {"name": "Pemberton Insurance", "sector": "financials", "weight_pct": 3.0},
            {"name": "Aurelia Utilities", "sector": "utilities", "weight_pct": 2.8},
        ],
    },
    # Edge case: sits exactly on the limits of Mandate 5 (risk 4, fee 1.10, top holding 5.0).
    5: {
        "id": 5,
        "name": "Meridian Balanced Multi-Asset",
        "strategy": "multi_asset",
        "region": "Global",
        "ongoing_charge_pct": 1.10,
        "risk_rating": 4,
        "esg_rating": "B",
        "inception_date": date(2015, 10, 2),
        "Percentage_of_fund_represented": 30.0,
        "NAV_per_share": [
            {"quarter": "Q1", "nav": 7.35},
            {"quarter": "Q2", "nav": 7.41},
            {"quarter": "Q3", "nav": 7.38},
            {"quarter": "Q4", "nav": 7.52},
        ],
        "holdings": [
            {"name": "Government of Alderland", "sector": "government", "weight_pct": 5.0},
            {"name": "Northbridge Software", "sector": "technology", "weight_pct": 4.5},
            {"name": "Calder Bank", "sector": "financials", "weight_pct": 4.2},
            {"name": "Helix Biopharma", "sector": "healthcare", "weight_pct": 3.8},
            {"name": "Orrin Consumer Brands", "sector": "consumer_discretionary", "weight_pct": 3.5},
            {"name": "Stanmore Industrial", "sector": "industrials", "weight_pct": 3.2},
            {"name": "Clearwater Utilities", "sector": "utilities", "weight_pct": 3.0},
            {"name": "Ridgeway Properties", "sector": "real_estate", "weight_pct": 2.8},
        ],
    },
    # Edge case: high fee, no ESG rating.
    6: {
        "id": 6,
        "name": "Meridian Active Thematic Equity",
        "strategy": "equity",
        "region": "Global",
        "ongoing_charge_pct": 2.25,
        "risk_rating": 5,
        "esg_rating": "unrated",
        "inception_date": date(2019, 2, 25),
        "Percentage_of_fund_represented": 37.5,
        "NAV_per_share": [
            {"quarter": "Q1", "nav": 1.92},
            {"quarter": "Q2", "nav": 2.08},
            {"quarter": "Q3", "nav": 1.85},
            {"quarter": "Q4", "nav": 1.71},
        ],
        "holdings": [
            {"name": "Quantis AI Systems", "sector": "technology", "weight_pct": 9.5},
            {"name": "Neuronex Robotics", "sector": "technology", "weight_pct": 8.0},
            {"name": "Cipher Payments", "sector": "financials", "weight_pct": 6.0},
            {"name": "GeneWave Therapeutics", "sector": "healthcare", "weight_pct": 5.5},
            {"name": "Orbital Logistics", "sector": "industrials", "weight_pct": 4.5},
            {"name": "StreamHub Media", "sector": "telecommunications", "weight_pct": 4.0},
        ],
    },
    # Edge case: highest risk rating, weakest ESG.
    7: {
        "id": 7,
        "name": "Meridian Frontier Markets",
        "strategy": "emerging_markets",
        "region": "Frontier Markets",
        "ongoing_charge_pct": 1.95,
        "risk_rating": 7,
        "esg_rating": "D",
        "inception_date": date(2012, 4, 30),
        "Percentage_of_fund_represented": 41,
        "NAV_per_share": [
            {"quarter": "Q1", "nav": 1.58},
            {"quarter": "Q2", "nav": 1.49},
            {"quarter": "Q3", "nav": 1.37},
            {"quarter": "Q4", "nav": 1.41},
        ],
        "holdings": [
            {"name": "Sahel Oil and Gas", "sector": "fossil_fuels", "weight_pct": 10.5},
            {"name": "Delta Petroleum", "sector": "fossil_fuels", "weight_pct": 7.0},
            {"name": "Kilimanjaro Bank", "sector": "financials", "weight_pct": 6.5},
            {"name": "Savanna Telecom", "sector": "telecommunications", "weight_pct": 5.5},
            {"name": "Tashkent Mining", "sector": "materials", "weight_pct": 5.0},
            {"name": "Casa Royale Gaming", "sector": "gambling", "weight_pct": 4.0},
            {"name": "Caspian Arms Manufacturing", "sector": "weapons", "weight_pct": 2.5},
        ],
    },
}


# ---------------------------------------------------------------------------
# CLIENTS
# risk_tolerance: highest fund risk_rating allowed (1 to 7)
# min_esg_rating and max_ongoing_charge_pct may be None (no rule).
# ---------------------------------------------------------------------------
CLIENTS = {
    1: {
        "id": 1,
        "client_name": "Harrington Family Trust",
        "risk_tolerance": 5,
        "excluded_sectors": ["tobacco", "weapons"],
        "max_single_holding_pct": 8.0,
        "min_esg_rating": "B",
        "max_ongoing_charge_pct": 1.00,
        "notes": "Long-term growth for a multi-generational family trust. Trustees exclude tobacco and weapons.",
    },
    2: {
        "id": 2,
        "client_name": "Oakridge Pension Scheme",
        "risk_tolerance": 3,
        "excluded_sectors": [],
        "max_single_holding_pct": 5.0,
        "min_esg_rating": None,
        "max_ongoing_charge_pct": 0.60,
        "notes": "Capital preservation for a closed defined-benefit scheme. Low cost and low risk are the priorities.",
    },
    # Edge case: strict ethical mandate, Meridian Sustainable Global Equity is fully compliant.
    3: {
        "id": 3,
        "client_name": "Whitmore Foundation",
        "risk_tolerance": 4,
        "excluded_sectors": ["tobacco", "weapons", "fossil_fuels", "gambling"],
        "max_single_holding_pct": 6.0,
        "min_esg_rating": "B",
        "max_ongoing_charge_pct": 0.80,
        "notes": "Charitable endowment with a strict ethical policy. Grants are funded from the income.",
    },
    4: {
        "id": 4,
        "client_name": "Castellan Growth Partners",
        "risk_tolerance": 6,
        "excluded_sectors": ["gambling"],
        "max_single_holding_pct": 10.0,
        "min_esg_rating": None,
        "max_ongoing_charge_pct": None,
        "notes": "Family office with a high risk appetite and no fee ceiling. Only gambling is excluded.",
    },
    # Edge case: limits sit exactly on Meridian Balanced Multi-Asset (risk 4, fee 1.10, top holding 5.0).
    5: {
        "id": 5,
        "client_name": "Dr Ingrid Lindqvist",
        "risk_tolerance": 4,
        "excluded_sectors": ["tobacco"],
        "max_single_holding_pct": 5.0,
        "min_esg_rating": "C",
        "max_ongoing_charge_pct": 1.10,
        "notes": "Private client approaching retirement. Moderate risk, avoids tobacco for personal reasons.",
    },
}

# ---------------------------------------------------------------------------
# Portfolios
# positions: fund_id must exist in FUNDS, weights sum to at most 100
# ---------------------------------------------------------------------------
PORTFOLIOS = {
    1: {
        "id": 1,
        "positions": [
            {"fund_id": 1, "weight_pct": 50.0},
            {"fund_id": 3, "weight_pct": 30.0},
            {"fund_id": 4, "weight_pct": 20.0},
        ],
    },
    2: {
        "id": 2,
        "positions": [
            {"fund_id": 4, "weight_pct": 70.0},
            {"fund_id": 5, "weight_pct": 30.0},
        ],
    },
    3: {
        "id": 3,
        "positions": [
            {"fund_id": 3, "weight_pct": 60.0},
            {"fund_id": 4, "weight_pct": 20.0},
            {"fund_id": 5, "weight_pct": 20.0},
        ],
    },
    # 10% cash.
    4: {
        "id": 4,
        "positions": [
            {"fund_id": 1, "weight_pct": 30.0},
            {"fund_id": 2, "weight_pct": 30.0},
            {"fund_id": 6, "weight_pct": 20.0},
            {"fund_id": 7, "weight_pct": 10.0},
        ],
    },
    # Edge case: 15% in the emerging markets fund gives 0.45% look-through tobacco exposure.
    5: {
        "id": 5,
        "positions": [
            {"fund_id": 5, "weight_pct": 60.0},
            {"fund_id": 3, "weight_pct": 25.0},
            {"fund_id": 2, "weight_pct": 15.0},
        ],
    },
}
