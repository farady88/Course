"""Documents for the knowledge base. All documents are synthetic.

Each document has: id, title, doc_type, date, fund_id (optional) and text.
"""

from datetime import date

# Document types: factsheet, commentary, agreement, policy, rules, disclosure
DOCUMENTS = {
    1: {
        "id": 1,
        "title": "Meridian Global Equity Growth Fund Factsheet",
        "doc_type": "factsheet",
        "date": date(2024, 3, 31),
        "fund_id": 1,
        "text": """MERIDIAN GLOBAL EQUITY GROWTH FUND
Fact Sheet as of March 31, 2024

Fund Overview
Strategy: Equity
Region: Global
Inception Date: March 17, 2014
Ongoing Charge: 0.85%
Risk Rating: 5/7
ESG Rating: B

Performance (NAV per share)
Q1 2024: £3.82
Q2 2024: £3.95
Q3 2024: £4.08
Q4 2024: £4.21

Top Holdings
1. Northbridge Software (Technology) - 7.5%
2. Aurelia Semiconductors (Technology) - 6.8%
3. Calder Bank (Financials) - 5.2%
4. Helix Biopharma (Healthcare) - 5.0%
5. Vantor Cloud (Technology) - 4.6%
6. Pemberton Insurance (Financials) - 4.1%
7. Orrin Consumer Brands (Consumer Discretionary) - 3.9%
8. Stanmore Industrial (Industrials) - 3.6%
9. Lumen Health Devices (Healthcare) - 3.4%
10. Tessaly Retail (Consumer Discretionary) - 3.0%

Total Represented by Holdings: 47.1%
"""
    },
    2: {
        "id": 2,
        "title": "Meridian Emerging Markets Equity Fund Factsheet",
        "doc_type": "factsheet",
        "date": date(2024, 3, 31),
        "fund_id": 2,
        "text": """MERIDIAN EMERGING MARKETS EQUITY FUND
Fact Sheet as of March 31, 2024

Fund Overview
Strategy: Emerging Markets
Region: Emerging Markets
Inception Date: September 5, 2011
Ongoing Charge: 1.45%
Risk Rating: 6/7
ESG Rating: C

Performance (NAV per share)
Q1 2024: £2.46
Q2 2024: £2.38
Q3 2024: £2.51
Q4 2024: £2.44

Top Holdings
1. Jade Dragon Electronics (Technology) - 8.2%
2. Bharat Private Bank (Financials) - 6.5%
3. Costa Verde Mining (Materials) - 5.4%
4. Pampas Energy (Fossil Fuels) - 4.8%
5. Sunrise Telecom (Telecommunications) - 4.4%
6. Ankara Retail Group (Consumer Discretionary) - 4.0%
7. Lagos Cement (Materials) - 3.6%
8. Andes Utilities (Utilities) - 3.2%
9. Mekong Consumer Staples (Consumer Staples) - 3.1%
10. Kestrel Tobacco Holdings (Tobacco) - 3.0%

Total Represented by Holdings: 46.2%
Note: This fund contains 3% tobacco exposure.
"""
    },
    3: {
        "id": 3,
        "title": "Q1 2024 Manager Commentary - Global Equity Growth",
        "doc_type": "commentary",
        "date": date(2024, 1, 31),
        "fund_id": 1,
        "text": """MERIDIAN GLOBAL EQUITY GROWTH FUND
Quarterly Manager Commentary - Q1 2024

Dear Investors,

I am pleased to report that the Meridian Global Equity Growth Fund delivered strong performance in Q1 2024, with the NAV per share increasing from £3.65 at year-end 2023 to £3.82 by March 31, 2024, representing a 4.7% quarterly return.

The fund's outperformance was driven primarily by our technology holdings, particularly Northbridge Software and Aurelia Semiconductors, which benefited from strong earnings reports and positive industry trends. Our overweight position in healthcare also contributed positively, with Helix Biopharma exceeding expectations.

Geographically, our U.S. and European exposures were the strongest performers, while Asian markets showed more modest gains. The fund's global diversification helped mitigate regional volatility.

Looking ahead, we remain confident in our growth-oriented approach and see continued opportunities in innovation-driven sectors. The fund maintains its characteristic balance between established leaders and emerging growth companies.

Thank you for your continued trust in our management team.

Best regards,
Henry Meridian
Fund Manager, Meridian Global Equity Growth
"""
    },
    4: {
        "id": 4,
        "title": "Q3 2023 Manager Commentary - Emerging Markets (Underperformance Explanation)",
        "doc_type": "commentary",
        "date": date(2023, 9, 30),
        "fund_id": 2,
        "text": """MERIDIAN EMERGING MARKETS EQUITY FUND
Quarterly Manager Commentary - Q3 2023

Dear Investors,

I am writing to address the Meridian Emerging Markets Equity Fund's underperformance in Q3 2023, during which the NAV per share declined from £2.58 to £2.51, a 2.7% decrease.

The primary factors contributing to this underperformance were:

1. **Commodity Price Volatility**: Our significant exposure to materials and energy sectors (Costa Verde Mining and Pampas Energy, representing 10.2% of the fund) suffered from declining commodity prices amid global growth concerns.

2. **Currency Headwinds**: Emerging market currencies faced pressure against the U.S. dollar, particularly affecting our holdings in Brazil (Bharat Private Bank) and South Africa (Lagos Cement).

3. **Geopolitical Tensions**: Rising tensions in Eastern Europe and the Middle East created risk-off sentiment that disproportionately impacted emerging markets.

4. **Selective Holding Performance**: While our technology positions (Jade Dragon Electronics) performed adequately, they were insufficient to offset the challenges in other sectors.

We have taken several steps to address these challenges:
- Reduced our materials exposure from 9.0% to 5.4%
- Increased our telecommunications weighting to improve defensive characteristics
- Maintained our strict ESG oversight, though we note the fund's inherent 3% tobacco exposure as outlined in our investment mandate

We believe these adjustments position the fund for recovery as global growth stabilizes and emerging market valuations become more attractive.

Please do not hesitate to contact us with any questions.

Sincerely,
Henry Meridian
Fund Manager, Meridian Emerging Markets Equity
"""
    },
    5: {
        "id": 5,
        "title": "Investment Management Agreement - Harrington Family Trust",
        "doc_type": "agreement",
        "date": date(2020, 6, 15),
        "fund_id": None,
        "text": """INVESTMENT MANAGEMENT AGREEMENT

This Investment Management Agreement ("Agreement") is made effective as of June 15, 2020, by and between:

CLIENT: Harrington Family Trust (Client ID: 1)
ADVISOR: Meridian Asset Management Advisors

1. SCOPE OF SERVICES
Meridian Asset Management Advisors shall provide investment advisory services to the Harrington Family Trust, including portfolio construction, ongoing management, and performance reporting.

2. INVESTMENT OBJECTIVES AND RESTRICTIONS
The Client has specified the following investment parameters:
- Risk Tolerance: 5 (on scale of 1-7)
- Excluded Sectors: Tobacco, Weapons
- Maximum Single Holding Percentage: 8.0%
- Minimum ESG Rating: B
- Maximum Ongoing Charge Percentage: 1.00%
- Notes: Long-term growth for a multi-generational family trust. Trustees exclude tobacco and weapons.

3. INVESTMENT APPROACH
The Advisor shall construct and manage a portfolio consistent with the Client's stated restrictions and objectives, utilizing Meridian's range of investment funds where appropriate.

4. FEES
Advisory fees shall be 0.25% annually of assets under management, payable quarterly in arrears.

5. REPORTING
The Advisor shall provide quarterly performance reports and an annual comprehensive review.

6. TERM AND TERMINATION
This Agreement shall continue until terminated by either party upon 90 days' written notice.

IN WITNESS WHEREOF, the parties have executed this Agreement as of the date first written above.

_________________________
Harrington Family Trust Representative

_________________________
Meridian Asset Management Advisors Representative
"""
    },
    6: {
        "id": 6,
        "title": "Meridian ESG and Exclusions Policy",
        "doc_type": "policy",
        "date": date(2023, 1, 10),
        "fund_id": None,
        "text": """MERIDIAN ASSET MANAGEMENT
ESG AND EXCLUSIONS POLICY
Effective January 10, 2023

1. PURPOSE
This policy outlines Meridian Asset Management's approach to environmental, social, and governance (ESG) considerations and application of exclusions across our investment platform.

2. ESG INTEGRATION APPROACH
Meridian employs an integrated ESG approach where ESG factors are considered alongside traditional financial analysis in our investment decision-making process. We believe that material ESG factors can impact long-term investment performance.

3. ESG RATING SYSTEM
We utilize a five-tier ESG rating system:
- A: Excellent (Leader in ESG practices)
- B: Good (Above average ESG integration)
- C: Moderate (Average ESG consideration)
- D: Below Average (Limited ESG integration)
- Unrated: Insufficient data for rating

4. EXCLUSIONS POLICY
Meridian applies the following product-based exclusions across all managed portfolios unless specifically exempted by client mandate:
- Tobacco: 0% revenue threshold
- Weapons: 0% revenue threshold (including firearms, ammunition, and military equipment)
- Thermal Coal: 10% revenue threshold (for electricity generation)

Client-specific exclusions may be applied in addition to our baseline policy, as demonstrated in individual client mandates.

5. IMPLEMENTATION AND MONITORING
ESG ratings are reviewed quarterly. Exclusion compliance is monitored daily through our automated screening systems. Violations trigger immediate review and typically require divestment within 5 business days.

6. ENGAGEMENT AND STEWARDSHIP
Where appropriate, Meridian engages with portfolio companies on ESG matters through dialogue and, when necessary, shareholder resolutions.

7. GOVERNANCE
The Meridian ESG Committee oversees policy implementation and reports quarterly to the Board of Directors.

Questions regarding this policy should be directed to the Meridian ESG Committee.
"""
    },
    7: {
        "id": 7,
        "title": "Suitability Rules Summary for Retail Investors",
        "doc_type": "rules",
        "date": date(2022, 11, 5),
        "fund_id": None,
        "text": """MERIDIAN ASSET MANAGEMENT
SUITABILITY RULES SUMMARY
For Retail Investors - Effective November 5, 2022

OVERVIEW
These suitability rules ensure that investment recommendations align with clients' financial situations, investment objectives, and risk tolerance. All advisors must comply with these rules when making investment recommendations.

KEY COMPONENTS

1. KNOW YOUR CLIENT (KYC)
Before any investment recommendation, advisors must establish and document:
- Client identity and contact information
- Financial situation (assets, liabilities, income, expenses)
- Investment objectives and time horizon
- Risk tolerance and capacity for loss
- Knowledge and experience with investment products

2. RISK TOLERANCE ASSESSMENT
Risk tolerance is assessed on a scale of 1-7:
- 1-2: Conservative (Capital preservation focus)
- 3-4: Moderate (Balanced growth and preservation)
- 5-6: Aggressive (Growth focus with accepted volatility)
- 7: Very Aggressive (Maximum growth pursuit)

3. PRODUCT SUITABILITY MATRIX
Investment products must match client risk tolerance:
- Risk Rating 1-2: Suitable for funds with risk ratings 1-2 only
- Risk Rating 3-4: Suitable for funds with risk ratings 1-4
- Risk Rating 5-6: Suitable for funds with risk ratings 1-6
- Risk Rating 7: Suitable for all funds (1-7)

4. EXCLUSIONS AND RESTRICTIONS
All recommended investments must comply with:
- Client-specific excluded sectors
- Maximum single holding concentration limits
- Minimum ESG rating requirements
- Maximum ongoing charge percentage limits

5. DOCUMENTATION REQUIREMENTS
All suitability assessments must be documented in the client file, including:
- Reasoning behind recommendations
- How the recommendation suits the client profile
- Any limitations or qualifications

6. REVIEW CYCLE
Suitability assessments must be reviewed:
- Annually for all clients
- Upon any significant change in client circumstances
- Before implementing any new investment recommendation

COMPLIANCE
Failure to adhere to these suitability rules may result in disciplinary action, up to and including termination.

For questions, contact the Meridian Compliance Department.
"""
    },
    8: {
        "id": 8,
        "title": "Fee and Charges Disclosure Policy",
        "doc_type": "disclosure",
        "date": date(2023, 5, 20),
        "fund_id": None,
        "text": """MERIDIAN ASSET MANAGEMENT
FEE AND CHARGES DISCLOSURE POLICY
Effective May 20, 2023

1. PURPOSE
This policy ensures transparent and comprehensive disclosure of all fees and charges associated with Meridian's investment products and services, enabling clients to make informed decisions.

2. DISCLOSURE PRINCIPLES
All fee disclosures shall be:
- Clear and unambiguous
- Presented in a timely manner
- Provided in both percentage and monetary terms where applicable
- Updated promptly when changes occur
- Available in clients' preferred language

3. FUND-LEVEL DISCLOSURES
For each managed fund, we disclose:
- Ongoing Charge Figure (OCF): Annual fee covering management, administration, and operational costs
- Transaction Costs: Estimated costs associated with buying and selling fund holdings
- Incidental Costs: Performance fees (where applicable) and other irregular charges
- Total Estimated Charge: Sum of all above components

4. SERVICE-LEVEL DISCLOSURES
For advisory and management services, we disclose:
- Advisory Fee Percentage: Annual fee based on assets under management
- Minimum Fee Amounts: Any fixed minimum charges
- Additional Service Charges: For specialized reporting or consulting
- Third-Party Costs: Custody, audit, or other external service fees passed through to clients

5. COMMUNICATION METHODS
Fee information is provided through:
- Product fact sheets and fund documentation
- Client onboarding materials
- Quarterly and annual statements
- Dedicated fee illustration documents upon request
- Our secure client portal
- Annual general meetings

6. REVIEW AND UPDATES
Fee structures are reviewed annually. Any changes to fee schedules provide clients with minimum 60 days' notice before implementation.

7. COMPARISON TOOLS
We provide fee comparison tools showing:
- Our fees versus industry averages
- Impact of fees on long-term investment returns
- Scenario analysis for different investment horizons

For detailed fee information on any specific product or service, please contact our Client Relations team or consult your financial advisor.
"""
    }
}