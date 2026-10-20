"""Evaluation questions for the synthetic Meridian portfolio-management knowledge base.

The question themes were informed by the external research sources listed in
RESEARCH_SOURCES. Expected evidence, keywords, and doc_id values for answerable
questions are grounded in docs.py only. Questions q41-q50 intentionally ask for
facts that the supplied knowledge base does not establish and should be refused
or answered with a clear statement that the evidence is insufficient.

Expected item schema:
    {
        "id": str,
        "question": str,
        "doc_id": str | None,
        "evidence": str | None,
        "keywords": list[str],
        "kind": str,
    }

Keyword strings may include alternatives separated by "|", matching the style
of the user's examples (e.g. "11|eleven").
"""

EVAL_SET = [
    # ------------------------------------------------------------------
    # Answerable questions (40)
    # ------------------------------------------------------------------
    {
        "id": "q01",
        "question": "What is the investment objective of Meridian Global Equity Growth?",
        "doc_id": "doc-01",
        "evidence": "The fund seeks long-term capital growth through investment in a diversified portfolio of global equities.",
        "keywords": ["long-term capital growth", "global equities", "diversified"],
        "kind": "lookup",
    },
    {
        "id": "q02",
        "question": "What does Meridian Global Equity Growth assess before establishing a position, and why is strong growth alone insufficient?",
        "doc_id": "doc-01",
        "evidence": "Valuation is considered before a position is established; strong growth alone is not sufficient reason to buy a security.",
        "keywords": ["valuation", "not sufficient reason", "buy a security"],
        "kind": "title-dependent",
    },
    {
        "id": "q03",
        "question": "Under what circumstances may Meridian Global Equity Growth reduce or sell a position?",
        "doc_id": "doc-01",
        "evidence": "A position may be reduced or sold when the investment thesis deteriorates, valuation becomes difficult to justify, a better opportunity is identified, or portfolio risk becomes inconsistent with the mandate.",
        "keywords": ["investment thesis deteriorates", "valuation", "better opportunity", "portfolio risk"],
        "kind": "multi-hop",
    },
    {
        "id": "q04",
        "question": "Does the Meridian Global Equity Growth Reference Index require the fund to replicate the index's holdings?",
        "doc_id": "doc-01",
        "evidence": "The benchmark is a reference point for performance discussion; it does not mean that the portfolio must replicate the benchmark's holdings.",
        "keywords": ["no|not", "reference point", "does not mean", "replicate"],
        "kind": "negation",
    },
    {
        "id": "q05",
        "question": "What quarterly return did Meridian Global Equity Growth report for Q1 2024, and how did its NAV per share change?",
        "doc_id": "doc-08",
        "evidence": "The fund's NAV per share increased from £3.65 at year-end 2023 to £3.82 by 31 March 2024, representing a reported quarterly return of 4.7%.",
        "keywords": ["4.7%|4.7 percent", "£3.65", "£3.82"],
        "kind": "numeric",
    },
    {
        "id": "q06",
        "question": "Which holdings were named as benefiting from strong earnings reports and positive industry trends in Meridian Global Equity Growth's Q1 2024 commentary?",
        "doc_id": "doc-08",
        "evidence": "Northbridge Software and Aurelia Semiconductors benefited from strong earnings reports and positive industry trends.",
        "keywords": ["Northbridge Software", "Aurelia Semiconductors"],
        "kind": "title-dependent",
    },
    {
        "id": "q07",
        "question": "What NAV-per-share decline and reported percentage decrease did Meridian Emerging Markets Equity experience in Q3 2023?",
        "doc_id": "doc-09",
        "evidence": "The NAV per share declined from £2.58 to £2.51 during the quarter, a reported 2.7% decrease.",
        "keywords": ["£2.58", "£2.51", "2.7%|2.7 percent", "decrease|declined"],
        "kind": "numeric",
    },
    {
        "id": "q08",
        "question": "How did the manager change Meridian Emerging Markets Equity's materials exposure during Q3 2023?",
        "doc_id": "doc-09",
        "evidence": "The manager reported reducing materials exposure from 9.0% to 5.4% and increasing telecommunications weighting to improve defensive characteristics.",
        "keywords": ["9.0%", "5.4%", "reducing materials", "increasing telecommunications"],
        "kind": "numeric",
    },
    {
        "id": "q09",
        "question": "What are the main sources of risk identified for Meridian Emerging Markets Equity?",
        "doc_id": "doc-02",
        "evidence": "The strategy is exposed to:\n- emerging-market equity volatility;\n- foreign-exchange movements;\n- commodity-price cycles;\n- political and regulatory changes;\n- liquidity differences between markets;\n- concentrated country or sector opportunities.",
        "keywords": ["equity volatility", "foreign-exchange", "commodity-price", "political", "liquidity", "concentrated country or sector"],
        "kind": "lookup",
    },
    {
        "id": "q10",
        "question": "What reported tobacco exposure in Meridian Emerging Markets Equity must be considered when checking a client tobacco restriction?",
        "doc_id": "doc-02",
        "evidence": "The portfolio also contains a reported 3% holding in Kestrel Tobacco Holdings.",
        "keywords": ["3%", "Kestrel Tobacco Holdings", "tobacco"],
        "kind": "numeric",
    },
    {
        "id": "q11",
        "question": "What ESG rating is reported for Meridian Sustainable Global Equity, and does the listed-holdings information prove the complete portfolio has zero exposure to excluded sectors?",
        "doc_id": "doc-03",
        "evidence": "The structured record shows an ESG rating of A and reports no tobacco, weapons, fossil-fuel or gambling holdings among the listed positions. This is not, by itself, proof that the complete portfolio has zero exposure.",
        "keywords": ["A", "not|does not", "zero exposure", "listed positions"],
        "kind": "negation",
    },
    {
        "id": "q12",
        "question": "Does Meridian Sustainable Global Equity select companies solely because they have a strong sustainability profile?",
        "doc_id": "doc-03",
        "evidence": "Financial quality remains part of the investment decision; a company is not selected solely because it has a strong sustainability profile.",
        "keywords": ["no|not", "financial quality", "not selected solely"],
        "kind": "negation",
    },
    {
        "id": "q13",
        "question": "How does a longer duration generally affect a bond portfolio's sensitivity to market yields?",
        "doc_id": "doc-04",
        "evidence": "A longer duration generally means that a bond portfolio is more sensitive to changes in market yields.",
        "keywords": ["longer duration", "more sensitive", "market yields"],
        "kind": "definition",
    },
    {
        "id": "q14",
        "question": "What duration does the 2024 fixed-income risk report give for Meridian Global Government and Corporate Bond?",
        "doc_id": "doc-23",
        "evidence": "The structured record reports portfolio duration of 5.2 years.",
        "keywords": ["5.2 years", "5.2"],
        "kind": "numeric",
    },
    {
        "id": "q15",
        "question": "What yield-to-maturity is reported for Meridian Global Government and Corporate Bond, and is it a guaranteed investor return?",
        "doc_id": "doc-23",
        "evidence": "The structured record reports a 4.1% yield-to-maturity. Yield-to-maturity is a portfolio-level measure based on current holdings and assumptions. It is not a promise that an investor will earn exactly 4.1%.",
        "keywords": ["4.1%", "not|is not", "guaranteed|promise", "current holdings and assumptions"],
        "kind": "negation",
    },
    {
        "id": "q16",
        "question": "What percentage of Meridian Global Government and Corporate Bond is represented by its reported top position in Government of Alderland?",
        "doc_id": "doc-23",
        "evidence": "The reported top position is Government of Alderland at 12.0%.",
        "keywords": ["12.0%|12%", "Government of Alderland"],
        "kind": "numeric",
    },
    {
        "id": "q17",
        "question": "What investment objective does Meridian Balanced Multi-Asset seek?",
        "doc_id": "doc-05",
        "evidence": "The fund seeks balanced long-term capital growth and income by combining different asset and risk exposures.",
        "keywords": ["capital growth and income", "different asset and risk exposures"],
        "kind": "lookup",
    },
    {
        "id": "q18",
        "question": "Does diversification in Meridian Balanced Multi-Asset eliminate market risk?",
        "doc_id": "doc-05",
        "evidence": "Diversification can reduce dependence on a single asset class, but it does not eliminate market risk.",
        "keywords": ["no|not", "reduce dependence", "does not eliminate market risk"],
        "kind": "negation",
    },
    {
        "id": "q19",
        "question": "Which structural themes can Meridian Active Thematic Equity invest around?",
        "doc_id": "doc-06",
        "evidence": "The fund seeks long-term capital growth from companies expected to benefit from structural themes such as artificial intelligence, automation, digital payments, healthcare innovation and connected infrastructure.",
        "keywords": ["artificial intelligence", "automation", "digital payments", "healthcare innovation", "connected infrastructure"],
        "kind": "lookup",
    },
    {
        "id": "q20",
        "question": "Why can Meridian Active Thematic Equity be sensitive to market changes?",
        "doc_id": "doc-24",
        "evidence": "This can make the fund more sensitive to changes in valuation, adoption expectations and investor sentiment.",
        "keywords": ["valuation", "adoption expectations", "investor sentiment", "concentrated"],
        "kind": "causal",
    },
    {
        "id": "q21",
        "question": "What does an 'Unrated' ESG status mean under Meridian's ESG framework?",
        "doc_id": "doc-15",
        "evidence": "Unrated: insufficient data for an A-D rating.",
        "keywords": ["insufficient data", "A-D rating", "not a rating"],
        "kind": "definition",
    },
    {
        "id": "q22",
        "question": "What principal risks are associated with Meridian Frontier Markets?",
        "doc_id": "doc-07",
        "evidence": "The strategy can be affected by:\n- political and regulatory instability;\n- foreign-exchange movements;\n- lower market liquidity;\n- commodity dependence;\n- concentrated industries;\n- governance and disclosure differences;\n- abrupt changes in investor risk appetite.",
        "keywords": ["political", "foreign-exchange", "liquidity", "commodity", "governance", "risk appetite"],
        "kind": "lookup",
    },
    {
        "id": "q23",
        "question": "Which sectors are explicitly mentioned among Meridian Frontier Markets' reported holdings?",
        "doc_id": "doc-25",
        "evidence": "The listed holdings include fossil fuels, financials, telecommunications, materials, gambling and weapons.",
        "keywords": ["fossil fuels", "financials", "telecommunications", "materials", "gambling", "weapons"],
        "kind": "multi-hop",
    },
    {
        "id": "q24",
        "question": "What are the Harrington Family Trust's core fund restrictions for risk, excluded sectors, single-holding concentration, ESG rating and ongoing charges?",
        "doc_id": "doc-10",
        "evidence": "Risk tolerance: 5 on a 1-7 scale. - Excluded sectors: tobacco and weapons. - Maximum single holding: 8.0%. - Minimum ESG rating: B. - Maximum ongoing charge: 1.00%.",
        "keywords": ["5", "tobacco", "weapons", "8.0%", "B", "1.00%"],
        "kind": "multi-hop",
    },
    {
        "id": "q25",
        "question": "What is the Harrington Family Trust's advisory fee, when is it payable, and is it separate from fund ongoing charges?",
        "doc_id": "doc-10",
        "evidence": "The advisory fee is 0.25% annually of assets under management, payable quarterly in arrears. This advisory fee is separate from fund-level ongoing charges.",
        "keywords": ["0.25%", "quarterly in arrears", "separate", "fund-level ongoing charges"],
        "kind": "numeric",
    },
    {
        "id": "q26",
        "question": "What are the Oakridge Pension Scheme's maximum fund risk rating, maximum single-holding limit and maximum ongoing-charge limit?",
        "doc_id": "doc-11",
        "evidence": "- Maximum fund risk rating: 3.\n- No client-specific sector exclusions.\n- Maximum single holding: 5.0%.\n- No minimum ESG rating specified in the client record.\n- Maximum ongoing charge: 0.60%.",
        "keywords": ["3", "5.0%", "0.60%"],
        "kind": "multi-hop",
    },
    {
        "id": "q27",
        "question": "Which sectors does the Whitmore Foundation exclude, and what are its maximum holding, minimum ESG rating and ongoing-charge limit?",
        "doc_id": "doc-12",
        "evidence": "- Maximum fund risk rating: 4. - Excluded sectors: tobacco, weapons, fossil fuels and gambling. - Maximum single holding: 6.0%. - Minimum ESG rating: B. - Maximum ongoing charge: 0.80%.",
        "keywords": ["tobacco", "weapons", "fossil fuels", "gambling", "6.0%", "B", "0.80%"],
        "kind": "multi-hop",
    },
    {
        "id": "q28",
        "question": "What hard sector restriction applies to Castellan Growth Partners, and what are its maximum fund risk rating and single-holding limit?",
        "doc_id": "doc-13",
        "evidence": "- Maximum fund risk rating: 6. - Excluded sector: gambling. - Maximum single holding: 10.0%.",
        "keywords": ["gambling", "6", "10.0%"],
        "kind": "multi-hop",
    },
    {
        "id": "q29",
        "question": "For Dr Ingrid Lindqvist's mandate, do values equal to the maximum limits for fund risk rating, ongoing charge and top holding breach the screening rules?",
        "doc_id": "doc-14",
        "evidence": "The screening convention is that a value equal to a maximum is permitted; only a value above the maximum breaches it.",
        "keywords": ["no|do not", "equal", "permitted", "above the maximum"],
        "kind": "negation",
    },
    {
        "id": "q30",
        "question": "What do ESG ratings A, B, C, D and Unrated mean in Meridian's policy?",
        "doc_id": "doc-15",
        "evidence": "- A: Excellent - B: Good - C: Moderate - D: Below Average - Unrated: insufficient data for an A-D rating.",
        "keywords": ["A: Excellent", "B: Good", "C: Moderate", "D: Below Average", "Unrated: insufficient data"],
        "kind": "definition",
    },
    {
        "id": "q31",
        "question": "What baseline revenue thresholds does Meridian's ESG policy apply to tobacco, weapons and thermal coal used for electricity generation?",
        "doc_id": "doc-15",
        "evidence": "- Tobacco: 0% revenue threshold. - Weapons: 0% revenue threshold, including firearms, ammunition and military equipment. - Thermal coal used for electricity generation: 10% revenue threshold.",
        "keywords": ["tobacco", "0%", "weapons", "thermal coal", "10%"],
        "kind": "numeric",
    },
    {
        "id": "q32",
        "question": "How often does Meridian monitor exclusion compliance, and what normally follows a detected violation?",
        "doc_id": "doc-15",
        "evidence": "Exclusion compliance is monitored daily through automated screening. A detected violation triggers immediate review and normally requires divestment within five business days.",
        "keywords": ["daily", "automated screening", "immediate review", "five business days"],
        "kind": "lookup",
    },
    {
        "id": "q33",
        "question": "How does Meridian's suitability methodology classify client risk scores of 1-2, 3-4, 5-6 and 7?",
        "doc_id": "doc-16",
        "evidence": "- 1-2: Conservative - 3-4: Moderate - 5-6: Aggressive - 7: Very Aggressive",
        "keywords": ["1-2 Conservative", "3-4 Moderate", "5-6 Aggressive", "7 Very Aggressive"],
        "kind": "lookup",
    },
    {
        "id": "q34",
        "question": "Under Meridian's suitability mapping, which fund risk ratings may be considered for a client with risk score 5 or 6?",
        "doc_id": "doc-16",
        "evidence": "Client risk 5-6: funds rated 1-6.",
        "keywords": ["1-6", "funds rated"],
        "kind": "lookup",
    },
    {
        "id": "q35",
        "question": "Does a fund that passes Meridian's mechanical screening checks automatically become suitable for every aspect of a client's circumstances?",
        "doc_id": "doc-16",
        "evidence": "A fund passing these mechanical checks is not automatically suitable in every respect. A suitability assessment may require financial circumstances, capacity for loss, time horizon, knowledge and experience and other information outside this synthetic dataset.",
        "keywords": ["no|not", "not automatically suitable", "capacity for loss", "time horizon", "knowledge and experience"],
        "kind": "negation",
    },
    {
        "id": "q36",
        "question": "What priority order does Meridian specify for legal requirements, firm policy, client restrictions, fund mandates and qualitative preferences?",
        "doc_id": "doc-17",
        "evidence": "1.Applicable legal or regulatory requirements. 2.Firm-wide mandatory policy. 3.Client-specific contractual restrictions. 4.Fund-specific investment mandate. 5.Portfolio construction preferences and qualitative objectives.",
        "keywords": ["legal or regulatory", "firm-wide mandatory policy", "client-specific", "fund-specific", "qualitative objectives"],
        "kind": "lookup",
    },
    {
        "id": "q37",
        "question": "If a current structured record conflicts with descriptive prose, which source should the exact compliance calculation use?",
        "doc_id": "doc-17",
        "evidence": "Where a current structured record conflicts with descriptive prose in a document, exact compliance calculations must use the current structured record.",
        "keywords": ["current structured record", "exact compliance calculations", "not descriptive prose"],
        "kind": "policy",
    },
    {
        "id": "q38",
        "question": "Can the listed top holdings be used to conclude that an unlisted sector has zero total exposure or to establish a complete sector total?",
        "doc_id": "doc-18",
        "evidence": "A sector total may only be described as a complete fund-level sector exposure when a complete holdings dataset or an explicit aggregate exposure field is available. Summing listed holdings can establish a minimum represented exposure, not necessarily total exposure.",
        "keywords": ["no|not", "complete holdings dataset", "minimum represented exposure", "not necessarily total exposure"],
        "kind": "negation",
    },
    {
        "id": "q39",
        "question": "How does Meridian define the look-through exposure of a portfolio to an underlying fund holding?",
        "doc_id": "doc-18",
        "evidence": "For a portfolio position with weight P and a fund holding with weight H, the effective portfolio exposure is calculated as: P * H / 100",
        "keywords": ["P * H / 100", "portfolio position", "fund holding", "effective portfolio exposure"],
        "kind": "numeric",
    },
    {
        "id": "q40",
        "question": "When screening a fund against a client's maximum ongoing charge, should the advisory fee be added to the fund OCF?",
        "doc_id": "doc-19",
        "evidence": "When comparing a fund against a client's maximum ongoing charge, use the structured fund record's ongoing_charge_pct. Do not add a client advisory fee to the fund OCF unless the question specifically asks for total client cost.",
        "keywords": ["no|not", "ongoing_charge_pct", "do not add", "total client cost"],
        "kind": "policy",
    },

    # ------------------------------------------------------------------
    # Intentionally unanswerable / refusal tests (10)
    # ------------------------------------------------------------------
    {
        "id": "q41",
        "question": "What was Meridian Global Equity Growth's exact full-year 2024 return relative to its benchmark?",
        "doc_id": None,
        "evidence": None,
        "keywords": [],
        "kind": "unanswerable",
    },
    {
        "id": "q42",
        "question": "What was Meridian Global Equity Growth's complete fund-level technology-sector exposure on 31 December 2024, including unlisted positions?",
        "doc_id": None,
        "evidence": None,
        "keywords": [],
        "kind": "unanswerable",
    },
    {
        "id": "q43",
        "question": "What exact factors caused Meridian Active Thematic Equity's NAV to move in each quarter of 2024?",
        "doc_id": None,
        "evidence": None,
        "keywords": [],
        "kind": "unanswerable",
    },
    {
        "id": "q44",
        "question": "What is the complete maturity ladder and average maturity of Meridian Global Government and Corporate Bond?",
        "doc_id": None,
        "evidence": None,
        "keywords": [],
        "kind": "unanswerable",
    },
    {
        "id": "q45",
        "question": "What percentage of Meridian Global Government and Corporate Bond is assigned to each credit-rating category?",
        "doc_id": None,
        "evidence": None,
        "keywords": [],
        "kind": "unanswerable",
    },
    {
        "id": "q46",
        "question": "How many years remain until Dr Ingrid Lindqvist expects to retire?",
        "doc_id": None,
        "evidence": None,
        "keywords": [],
        "kind": "unanswerable",
    },
    {
        "id": "q47",
        "question": "What is the exact currency breakdown of Meridian Global Government and Corporate Bond by currency and percentage weight?",
        "doc_id": None,
        "evidence": None,
        "keywords": [],
        "kind": "unanswerable",
    },
    {
        "id": "q48",
        "question": "What return will Meridian Emerging Markets Equity deliver next quarter?",
        "doc_id": None,
        "evidence": None,
        "keywords": [],
        "kind": "unanswerable",
    },
    {
        "id": "q49",
        "question": "What is Meridian Frontier Markets' exact total portfolio exposure to gambling, including holdings omitted from the top-holdings list?",
        "doc_id": None,
        "evidence": None,
        "keywords": [],
        "kind": "unanswerable",
    },
    {
        "id": "q50",
        "question": "How much cash does the Harrington Family Trust need to withdraw from the portfolio each year?",
        "doc_id": None,
        "evidence": None,
        "keywords": [],
        "kind": "unanswerable",
    },
]

# External research informed the coverage and phrasing of question types; it is
# not used as expected-answer evidence. Answerable evaluation evidence above
# must be retrieved from docs.py, not from these external pages.
RESEARCH_SOURCES = [
    {
        "title": "A Quick Guide to Asset and Portfolio Management",
        "publisher": "Holborn Assets",
        "published": "10 November 2025",
        "url": "https://holbornassets.com/blog/a-quick-guide-to-asset-and-portfolio-management/",
        "topics_used": ["asset allocation", "risk management", "diversification", "rebalancing", "client risk tolerance"],
    },
    {
        "title": "Basics of Portfolio Planning and Construction",
        "publisher": "CFA Institute",
        "published": "2026 curriculum reading",
        "url": "https://www.cfainstitute.org/insights/professional-learning/refresher-readings/2026/basics-of-portfolio-planning-and-construction",
        "topics_used": ["client objectives and constraints", "investment policy statements", "risk and return", "asset allocation", "ESG preferences"],
    },
    {
        "title": "Assessing suitability",
        "publisher": "UK Financial Conduct Authority (FCA)",
        "url": "https://www.fca.org.uk/firms/assessing-suitability",
        "topics_used": ["client financial situation", "investment objectives", "risk profile", "capacity for loss", "knowledge and experience"],
    },
    {
        "title": "Knowing your customer and assessing their needs",
        "publisher": "UK Financial Conduct Authority (FCA)",
        "url": "https://www.fca.org.uk/firms/knowing-customer-assessing-needs",
        "topics_used": ["investment purpose and horizon", "risk profile", "financial situation", "investment knowledge and experience"],
    },
    {
        "title": "Mutual Funds",
        "publisher": "Investor.gov / U.S. Securities and Exchange Commission",
        "url": "https://www.investor.gov/introduction-investing/investing-basics/investment-products/mutual-funds-and-exchange-traded-funds-etfs/mutual-funds",
        "topics_used": ["fund objectives and risks", "fees and expenses", "NAV", "past performance limitations", "investor due diligence"],
    },
    {
        "title": "Standard III(C): Suitability",
        "publisher": "CFA Institute",
        "url": "https://www.cfainstitute.org/standards/professionals/code-ethics-standards/standards-of-practice-iii-c",
        "topics_used": ["matching investment characteristics to client constraints", "portfolio diversification", "client-specific suitability"],
    },
    {
        "title": "Standard III(A): Loyalty, Prudence, and Care",
        "publisher": "CFA Institute",
        "url": "https://www.cfainstitute.org/standards/professionals/code-ethics-standards/standards-of-practice-iii-a",
        "topics_used": ["client objectives and constraints", "diversification", "regular review", "disclosure and care"],
    },
]

# At-a-glance metadata useful to eval runners and reviewers.
EVAL_SET_SUMMARY = {
    "total_questions": len(EVAL_SET),
    "answerable_questions": sum(1 for item in EVAL_SET if item["kind"] != "unanswerable"),
    "unanswerable_questions": sum(1 for item in EVAL_SET if item["kind"] == "unanswerable"),
    "source_document_count": 25,
    "research_source_count": len(RESEARCH_SOURCES),
}

def answerable() -> list[dict]:
    return [q for q in EVAL_SET if q["doc_id"] is not None]


def unanswerable() -> list[dict]:
    return [q for q in EVAL_SET if q["doc_id"] is None]