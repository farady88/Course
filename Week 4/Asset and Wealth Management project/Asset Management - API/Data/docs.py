"""Synthetic investment documents for the vector knowledge base.

Design principles
-----------------
1.Structured records in records.py are authoritative for exact numerical facts:
   current fund charges, risk ratings, ESG ratings, holdings, weights, clients and
   portfolio positions.
2.These documents provide qualitative context: investment philosophy, process,
   risk methodology, benchmark definitions, performance attribution, mandates,
   policies and historical commentary.
3.Every document carries explicit temporal and authority metadata so retrieval can
   distinguish current snapshots from historical material.
4.Documents do not claim that a partial top-holdings list represents the whole fund.
5.Compliance decisions must remain deterministic in the mandate rules; these documents
   explain the rules but never replace the mandate rules.

All figures and entities are synthetic.
"""

from datetime import date

DOCUMENTS = {
    # -----------------------------------------------------------------------
    # FUND 1
    # -----------------------------------------------------------------------
    1: {
        "id": 1,
        "title": "Meridian Global Equity Growth - Investment Mandate and Philosophy",
        "doc_type": "fund_mandate",
        "document_date": date(2024, 12, 31),
        "effective_date": date(2024, 1, 1),
        "as_of_date": date(2024, 12, 31),
        "fund_id": 1,
        "client_id": None,
        "status": "active",
        "version": "1.0",
        "authority": "fund_management",
        "scope": "fund",
        "text": """MERIDIAN GLOBAL EQUITY GROWTH
INVESTMENT MANDATE AND PHILOSOPHY
Effective 1 January 2024 | Information as of 31 December 2024

## Investment objective
The fund seeks long-term capital growth through investment in a diversified
portfolio of global equities. The mandate prioritises companies where the
manager believes durable earnings growth is not fully reflected in market
expectations.

## Investment philosophy
The manager follows a fundamental, growth-oriented approach. The portfolio
combines established businesses with emerging growth companies. Particular
attention is given to companies with attractive long-term industry trends,
strong competitive positions, credible management teams and the ability to
reinvest capital at attractive rates.

## Investment process
The process has four stages:
1.The team identifies structural growth themes and industries with attractive
   long-term economics.
2.Individual companies are assessed using fundamental research, including
   earnings prospects, competitive position, balance-sheet strength and
   management quality.
3.Valuation is considered before a position is established; strong growth
   alone is not sufficient reason to buy a security.
4.Portfolio positions are reviewed as the investment thesis, valuation or
   risk changes.

## Portfolio construction
The portfolio is intentionally tilted toward companies with attractive growth
prospects. Technology and healthcare can become material sources of active
risk when the manager's research supports those positions. Diversification
across regions and industries is used to reduce dependence on any single
economic outcome.

## Sell discipline
A position may be reduced or sold when the investment thesis deteriorates,
valuation becomes difficult to justify, a better opportunity is identified,
or portfolio risk becomes inconsistent with the mandate.

## Benchmark
The fund reports against the Meridian Global Equity Growth Reference Index.
The benchmark is a reference point for performance discussion; it does not
mean that the portfolio must replicate the benchmark's holdings.

## Important limitation
The structured fund record contains the reported top holdings only. The
reported holdings therefore must not be treated as the fund's complete
portfolio or complete sector allocation."""
    },

    2: {
        "id": 2,
        "title": "Meridian Emerging Markets Equity - Investment Mandate and Risk Profile",
        "doc_type": "fund_mandate",
        "document_date": date(2024, 12, 31),
        "effective_date": date(2024, 1, 1),
        "as_of_date": date(2024, 12, 31),
        "fund_id": 2,
        "client_id": None,
        "status": "active",
        "version": "1.0",
        "authority": "fund_management",
        "scope": "fund",
        "text": """MERIDIAN EMERGING MARKETS EQUITY
INVESTMENT MANDATE AND RISK PROFILE
Effective 1 January 2024 | Information as of 31 December 2024

## Investment objective
The fund seeks long-term capital growth from companies operating in emerging
markets. The manager accepts higher market, currency and political risk in
exchange for access to companies and economies with higher structural growth
potential.

## Investment philosophy
The manager uses fundamental research with an emphasis on local market
knowledge. Opportunities are assessed in the context of company fundamentals,
industry structure, valuation, currency conditions and country-level risks.

## Key risk sources
The strategy is exposed to:
- emerging-market equity volatility;
- foreign-exchange movements;
- commodity-price cycles;
- political and regulatory changes;
- liquidity differences between markets;
- concentrated country or sector opportunities.

## Investment process
The manager first assesses the attractiveness of an industry and local
economic environment, then evaluates individual companies. Position sizing
reflects conviction together with liquidity and country risk. The manager
may reduce exposures when the fundamental thesis weakens or when portfolio
risk becomes excessive.

## ESG and exclusions
The fund has an ESG rating recorded in the structured fund data. The portfolio
also contains a reported 3% holding in Kestrel Tobacco Holdings. A portfolio
manager must therefore use the deterministic mandate rules when checking
this fund against a client-specific tobacco restriction.

## Benchmark
The fund reports against the Meridian Emerging Markets Equity Reference Index.
The benchmark is a comparison reference and does not establish suitability
for a particular client.

## Important limitation
The structured record contains top reported holdings rather than the complete
portfolio. Absence of a sector from the reported list does not establish zero
total exposure."""
    },

    3: {
        "id": 3,
        "title": "Meridian Sustainable Global Equity - Investment and Sustainability Framework",
        "doc_type": "fund_mandate",
        "document_date": date(2024, 12, 31),
        "effective_date": date(2024, 1, 1),
        "as_of_date": date(2024, 12, 31),
        "fund_id": 3,
        "client_id": None,
        "status": "active",
        "version": "1.0",
        "authority": "fund_management",
        "scope": "fund",
        "text": """MERIDIAN SUSTAINABLE GLOBAL EQUITY
INVESTMENT AND SUSTAINABILITY FRAMEWORK
Effective 1 January 2024 | Information as of 31 December 2024

## Investment objective
The fund seeks long-term capital growth through global equities while
integrating sustainability considerations into security selection.

## Investment philosophy
The manager seeks businesses whose products, services and operating practices
are considered compatible with long-term sustainable economic development.
Financial quality remains part of the investment decision; a company is not
selected solely because it has a strong sustainability profile.

## Sustainability process
The investment team considers material environmental, social and governance
factors alongside traditional financial analysis. Companies are assessed for
the quality of their business model, governance, sustainability practices and
ability to manage material long-term risks.

## Portfolio construction
The strategy favours companies contributing to areas such as renewable energy,
efficient infrastructure, healthcare and enabling technologies. Diversification
is maintained across industries and regions.

## Client-use note
The structured record shows an ESG rating of A and reports no tobacco, weapons,
fossil-fuel or gambling holdings among the listed positions. This is not, by
itself, proof that the complete portfolio has zero exposure. Exact compliance
against a client mandate must be determined by the mandate rules.

## Benchmark
The fund reports against the Meridian Sustainable Global Equity Reference Index,
a global equity comparison benchmark incorporating sustainability constraints."""
    },

    4: {
        "id": 4,
        "title": "Meridian Global Government and Corporate Bond - Fixed Income Framework",
        "doc_type": "fund_mandate",
        "document_date": date(2024, 12, 31),
        "effective_date": date(2024, 1, 1),
        "as_of_date": date(2024, 12, 31),
        "fund_id": 4,
        "client_id": None,
        "status": "active",
        "version": "1.0",
        "authority": "fund_management",
        "scope": "fund",
        "text": """MERIDIAN GLOBAL GOVERNMENT AND CORPORATE BOND
FIXED INCOME INVESTMENT FRAMEWORK
Effective 1 January 2024 | Information as of 31 December 2024

## Investment objective
The fund seeks income and capital stability through a diversified portfolio
of government and corporate bonds.

## Investment process
The manager evaluates interest-rate conditions, sovereign fundamentals,
corporate credit quality, spread compensation and liquidity. Portfolio
construction balances income generation against duration and credit risk.

## Interest-rate risk
Duration is a key measure of sensitivity to changes in interest rates. A
longer duration generally means that a bond portfolio is more sensitive to
changes in market yields. The structured record reports a duration figure for
this fund as of the portfolio snapshot.

## Credit risk
Government and corporate issuers can contribute different sources of risk.
Corporate positions introduce issuer and credit-spread risk in addition to
general interest-rate risk.

## Concentration
The structured record deliberately contains a 12% reported position in
Government of Alderland. This is important when testing client concentration
limits. The deterministic mandate rules, rather than the LLM, decide
whether that position breaches a particular client's limit.

## Benchmark
The fund reports against the Meridian Global Government and Corporate Bond
Reference Index, a global government and investment-grade corporate bond
benchmark.

## Important limitation
The listed securities are reported top positions and do not constitute a
complete maturity, duration, credit-quality or issuer breakdown."""
    },

    5: {
        "id": 5,
        "title": "Meridian Balanced Multi-Asset - Strategic Allocation Framework",
        "doc_type": "fund_mandate",
        "document_date": date(2024, 12, 31),
        "effective_date": date(2024, 1, 1),
        "as_of_date": date(2024, 12, 31),
        "fund_id": 5,
        "client_id": None,
        "status": "active",
        "version": "1.0",
        "authority": "fund_management",
        "scope": "fund",
        "text": """MERIDIAN BALANCED MULTI-ASSET
STRATEGIC ALLOCATION FRAMEWORK
Effective 1 January 2024 | Information as of 31 December 2024

## Investment objective
The fund seeks balanced long-term capital growth and income by combining
different asset and risk exposures.

## Investment approach
The manager combines equities, government securities, property-related
exposure and other diversified investments. Allocation decisions consider
economic conditions, valuation, expected returns and portfolio risk.

## Role in a portfolio
The strategy is designed to provide a middle ground between a concentrated
equity strategy and a capital-preservation strategy. Diversification can
reduce dependence on a single asset class, but it does not eliminate market
risk.

## Concentration and mandate use
The structured record reports a 5% position in Government of Alderland. It is
also deliberately configured so that its risk rating, fee and reported top
holding can sit exactly at the limits used in Client 5's screening test.
The mandate rules treat a value equal to a client's maximum as compliant;
only a value above the limit is a breach.

## Benchmark
The fund reports against the Meridian Balanced Multi-Asset Reference
Benchmark, a strategic multi-asset comparison benchmark."""
    },

    6: {
        "id": 6,
        "title": "Meridian Active Thematic Equity - Thematic Investment Framework",
        "doc_type": "fund_mandate",
        "document_date": date(2024, 12, 31),
        "effective_date": date(2024, 1, 1),
        "as_of_date": date(2024, 12, 31),
        "fund_id": 6,
        "client_id": None,
        "status": "active",
        "version": "1.0",
        "authority": "fund_management",
        "scope": "fund",
        "text": """MERIDIAN ACTIVE THEMATIC EQUITY
THEMATIC INVESTMENT FRAMEWORK
Effective 1 January 2024 | Information as of 31 December 2024

## Investment objective
The fund seeks long-term capital growth from companies expected to benefit
from structural themes such as artificial intelligence, automation, digital
payments, healthcare innovation and connected infrastructure.

## Investment philosophy
The strategy accepts greater company and theme concentration than a broad
global equity portfolio. The manager looks for businesses with strong
exposure to a long-duration structural theme and evidence that the theme can
translate into sustainable commercial growth.

## Risk characteristics
Thematic investing can create significant concentration in particular
industries, technologies and valuation regimes. Theme popularity can also
lead to rapid changes in market expectations.

## ESG information
The structured record currently classifies the fund as ESG unrated. Unrated
does not mean either good or bad ESG performance; it means the record does
not assign an A-D rating. Where a client has a minimum ESG rating requirement,
the mandate rules must apply that rule explicitly.

## Cost
The fund has a comparatively high ongoing charge in the structured records.
Exact fee compliance is a deterministic check, not an LLM judgement.

## Benchmark
The fund reports against the Meridian Active Thematic Equity Reference Index."""
    },

    7: {
        "id": 7,
        "title": "Meridian Frontier Markets - Frontier Markets Risk Framework",
        "doc_type": "fund_mandate",
        "document_date": date(2024, 12, 31),
        "effective_date": date(2024, 1, 1),
        "as_of_date": date(2024, 12, 31),
        "fund_id": 7,
        "client_id": None,
        "status": "active",
        "version": "1.0",
        "authority": "fund_management",
        "scope": "fund",
        "text": """MERIDIAN FRONTIER MARKETS
FRONTIER MARKETS RISK FRAMEWORK
Effective 1 January 2024 | Information as of 31 December 2024

## Investment objective
The fund seeks long-term capital growth from companies in frontier markets,
accepting substantial volatility, liquidity and country risk.

## Key risk sources
The strategy can be affected by:
- political and regulatory instability;
- foreign-exchange movements;
- lower market liquidity;
- commodity dependence;
- concentrated industries;
- governance and disclosure differences;
- abrupt changes in investor risk appetite.

## Portfolio characteristics
The structured record deliberately contains fossil-fuel, gambling and weapons
holdings and carries the highest fund risk rating in the seed data. These
facts are relevant to client screening but do not by themselves determine
whether a particular client can hold the fund.

## ESG
The structured record classifies the fund as ESG rating D. Client-specific
minimum ESG requirements must be checked against that structured value.

## Benchmark
The fund reports against the Meridian Frontier Markets Reference Index.

## Important limitation
The listed holdings are not the complete portfolio. Do not infer zero
exposure to a sector merely because that sector is absent from the listed
positions."""
    },

    # -----------------------------------------------------------------------
    # PERFORMANCE / HISTORICAL COMMENTARY
    # -----------------------------------------------------------------------
    8: {
        "id": 8,
        "title": "Q1 2024 Manager Commentary - Global Equity Growth",
        "doc_type": "commentary",
        "document_date": date(2024, 3, 31),
        "effective_date": date(2024, 3, 31),
        "as_of_date": date(2024, 3, 31),
        "fund_id": 1,
        "client_id": None,
        "status": "historical",
        "version": "1.0",
        "authority": "fund_management",
        "scope": "fund",
        "text": """MERIDIAN GLOBAL EQUITY GROWTH FUND
QUARTERLY MANAGER COMMENTARY - Q1 2024
As of 31 March 2024

The fund's NAV per share increased from £3.65 at year-end 2023 to £3.82 by
31 March 2024, representing a reported quarterly return of 4.7%.

## Performance drivers
Technology holdings were the principal source of outperformance. Northbridge
Software and Aurelia Semiconductors benefited from strong earnings reports
and positive industry trends. The fund's overweight position in healthcare
also contributed positively, with Helix Biopharma exceeding expectations.

## Geographic contribution
U.S. and European exposures were reported as the strongest performers, while
Asian markets showed more modest gains. The manager attributed part of the
fund's resilience to global diversification.

## Manager outlook
The manager remained confident in the growth-oriented approach and continued
to see opportunities in innovation-driven sectors. The portfolio was described
as maintaining a balance between established leaders and emerging growth
companies.

## Interpretation rule
These statements describe the manager's view at the date of the commentary.
They are historical commentary and must not be presented as a current
forecast or guarantee of future performance."""
    },

    9: {
        "id": 9,
        "title": "Q3 2023 Manager Commentary - Emerging Markets Underperformance",
        "doc_type": "commentary",
        "document_date": date(2023, 9, 30),
        "effective_date": date(2023, 9, 30),
        "as_of_date": date(2023, 9, 30),
        "fund_id": 2,
        "client_id": None,
        "status": "historical",
        "version": "1.0",
        "authority": "fund_management",
        "scope": "fund",
        "text": """MERIDIAN EMERGING MARKETS EQUITY FUND
QUARTERLY MANAGER COMMENTARY - Q3 2023
As of 30 September 2023

The NAV per share declined from £2.58 to £2.51 during the quarter, a reported
2.7% decrease.

## Performance attribution
1.Commodity price volatility affected materials and energy exposure. The
   commentary identifies Costa Verde Mining and Pampas Energy as part of the
   affected exposure.
2.Currency headwinds affected emerging-market holdings as local currencies
   came under pressure against the U.S. dollar.
3.Geopolitical tensions contributed to risk-off sentiment.
4.Technology exposure, including Jade Dragon Electronics, performed
   adequately but did not offset weakness elsewhere.

## Portfolio actions
The manager reported reducing materials exposure from 9.0% to 5.4% and
increasing telecommunications weighting to improve defensive characteristics.

## ESG
The manager explicitly noted the fund's 3% tobacco exposure. This historical
commentary should be read alongside the current structured holdings and the
current ESG/exclusions policy when assessing a mandate.

## Historical-use warning
This document explains the manager's Q3 2023 view. It is not evidence that
the same exposures or market conditions still apply at a later date."""
    },

    # -----------------------------------------------------------------------
    # CLIENT MANDATES
    # -----------------------------------------------------------------------
    10: {
        "id": 10,
        "title": "Investment Management Agreement - Harrington Family Trust",
        "doc_type": "client_agreement",
        "document_date": date(2020, 6, 15),
        "effective_date": date(2020, 6, 15),
        "as_of_date": date(2020, 6, 15),
        "fund_id": None,
        "client_id": 1,
        "status": "active",
        "version": "1.0",
        "authority": "client_mandate",
        "scope": "client",
        "text": """INVESTMENT MANAGEMENT AGREEMENT
HARRINGTON FAMILY TRUST - CLIENT ID 1
Effective 15 June 2020

## Objective
The mandate seeks long-term growth for a multi-generational family trust.

## Restrictions
- Risk tolerance: 5 on a 1-7 scale.
- Excluded sectors: tobacco and weapons.
- Maximum single holding: 8.0%.
- Minimum ESG rating: B.
- Maximum ongoing charge: 1.00%.

## Service
Meridian Asset Management Advisors provides portfolio construction, ongoing
management and performance reporting.

## Fees
The advisory fee is 0.25% annually of assets under management, payable
quarterly in arrears. This advisory fee is separate from fund-level ongoing
charges.

## Reporting and review
The client receives quarterly performance reports and an annual comprehensive
review.

## Mandate interpretation
The restrictions above are client-specific. They are not merely descriptions
of the client's preferences. Where the mandate rules check a fund or
portfolio against Client 1, these restrictions are the applicable client
limits."""
    },

    11: {
        "id": 11,
        "title": "Investment Mandate Summary - Oakridge Pension Scheme",
        "doc_type": "client_agreement",
        "document_date": date(2024, 1, 5),
        "effective_date": date(2024, 1, 5),
        "as_of_date": date(2024, 1, 5),
        "fund_id": None,
        "client_id": 2,
        "status": "active",
        "version": "1.0",
        "authority": "client_mandate",
        "scope": "client",
        "text": """OAKRIDGE PENSION SCHEME
CLIENT MANDATE SUMMARY - CLIENT ID 2
Effective 5 January 2024

## Objective
The scheme prioritises capital preservation and cost control for a closed
defined-benefit pension arrangement.

## Investment parameters
- Maximum fund risk rating: 3.
- No client-specific sector exclusions.
- Maximum single holding: 5.0%.
- No minimum ESG rating specified in the client record.
- Maximum ongoing charge: 0.60%.

## Interpretation
The absence of an ESG minimum does not mean ESG is irrelevant; it means this
client record does not impose an additional ESG threshold. Firm-wide policy
and other applicable restrictions remain relevant.

The maximum holding and fee limits are hard screening parameters. Equality
with a limit is not a breach; a value above the limit is a breach."""
    },

    12: {
        "id": 12,
        "title": "Investment Mandate Summary - Whitmore Foundation",
        "doc_type": "client_agreement",
        "document_date": date(2024, 1, 8),
        "effective_date": date(2024, 1, 8),
        "as_of_date": date(2024, 1, 8),
        "fund_id": None,
        "client_id": 3,
        "status": "active",
        "version": "1.0",
        "authority": "client_mandate",
        "scope": "client",
        "text": """WHITMORE FOUNDATION
CLIENT MANDATE SUMMARY - CLIENT ID 3
Effective 8 January 2024

## Objective
The foundation manages a charitable endowment and funds grants from investment
income. It therefore combines moderate risk tolerance with a strict ethical
mandate.

## Investment parameters
- Maximum fund risk rating: 4.
- Excluded sectors: tobacco, weapons, fossil fuels and gambling.
- Maximum single holding: 6.0%.
- Minimum ESG rating: B.
- Maximum ongoing charge: 0.80%.

## Interpretation
The sector exclusions are cumulative. A fund containing a reported holding
from any excluded sector requires deterministic screening before a compliance
conclusion is made.

The mandate's ethical restrictions are stricter than the firm's baseline
policy where applicable."""
    },

    13: {
        "id": 13,
        "title": "Investment Mandate Summary - Castellan Growth Partners",
        "doc_type": "client_agreement",
        "document_date": date(2024, 1, 10),
        "effective_date": date(2024, 1, 10),
        "as_of_date": date(2024, 1, 10),
        "fund_id": None,
        "client_id": 4,
        "status": "active",
        "version": "1.0",
        "authority": "client_mandate",
        "scope": "client",
        "text": """CASTELLAN GROWTH PARTNERS
CLIENT MANDATE SUMMARY - CLIENT ID 4
Effective 10 January 2024

## Objective
The family office has a high risk appetite and seeks long-term growth.

## Investment parameters
- Maximum fund risk rating: 6.
- Excluded sector: gambling.
- Maximum single holding: 10.0%.
- No minimum ESG rating specified.
- No maximum ongoing charge specified.

## Interpretation
The lack of a fee ceiling does not imply that costs should be ignored in
investment analysis. It means that this client record does not impose a
deterministic maximum fee rule.

The gambling exclusion remains a hard client restriction and must be checked
by the mandate rules."""
    },

    14: {
        "id": 14,
        "title": "Investment Mandate Summary - Dr Ingrid Lindqvist",
        "doc_type": "client_agreement",
        "document_date": date(2024, 1, 12),
        "effective_date": date(2024, 1, 12),
        "as_of_date": date(2024, 1, 12),
        "fund_id": None,
        "client_id": 5,
        "status": "active",
        "version": "1.0",
        "authority": "client_mandate",
        "scope": "client",
        "text": """DR INGRID LINDQVIST
CLIENT MANDATE SUMMARY - CLIENT ID 5
Effective 12 January 2024

## Objective
The client is approaching retirement and has a moderate risk profile. The
client specifically excludes tobacco for personal reasons.

## Investment parameters
- Maximum fund risk rating: 4.
- Excluded sector: tobacco.
- Maximum single holding: 5.0%.
- Minimum ESG rating: C.
- Maximum ongoing charge: 1.10%.

## Boundary conditions
The mandate is deliberately configured so that Meridian Balanced Multi-Asset
sits exactly at several limits: risk rating 4, ongoing charge 1.10% and a
reported 5.0% top holding. The screening convention is that a value equal to
a maximum is permitted; only a value above the maximum breaches it."""
    },

    # -----------------------------------------------------------------------
    # FIRM POLICIES AND METHODOLOGY
    # -----------------------------------------------------------------------
    15: {
        "id": 15,
        "title": "Meridian ESG and Exclusions Policy",
        "doc_type": "policy",
        "document_date": date(2023, 1, 10),
        "effective_date": date(2023, 1, 10),
        "as_of_date": date(2023, 1, 10),
        "fund_id": None,
        "client_id": None,
        "status": "active",
        "version": "1.0",
        "authority": "firm_policy",
        "scope": "firm",
        "text": """MERIDIAN ASSET MANAGEMENT
ESG AND EXCLUSIONS POLICY
Effective 10 January 2023

## Purpose
Meridian integrates ESG considerations with traditional financial analysis.

## ESG rating framework
- A: Excellent
- B: Good
- C: Moderate
- D: Below Average
- Unrated: insufficient data for an A-D rating.

## Baseline exclusions
Unless a client mandate or other applicable rule requires a stricter
restriction, Meridian applies:
- Tobacco: 0% revenue threshold.
- Weapons: 0% revenue threshold, including firearms, ammunition and military
  equipment.
- Thermal coal used for electricity generation: 10% revenue threshold.

## Monitoring
ESG ratings are reviewed quarterly. Exclusion compliance is monitored daily
through automated screening. A detected violation triggers immediate review
and normally requires divestment within five business days.

## Client-specific restrictions
A client may have restrictions that are stricter than the baseline policy.
The client's mandate must therefore be considered alongside this policy.

## Important distinction
This policy defines the firm's framework. It does not calculate whether an
individual fund or portfolio breaches a client mandate. That determination is
performed by the deterministic mandate rules using structured records."""
    },

    16: {
        "id": 16,
        "title": "Meridian Suitability Rules and Product Risk Methodology",
        "doc_type": "rules",
        "document_date": date(2024, 1, 2),
        "effective_date": date(2024, 1, 2),
        "as_of_date": date(2024, 1, 2),
        "fund_id": None,
        "client_id": None,
        "status": "active",
        "version": "1.0",
        "authority": "firm_policy",
        "scope": "firm",
        "text": """MERIDIAN ASSET MANAGEMENT
SUITABILITY RULES AND PRODUCT RISK METHODOLOGY
Effective 2 January 2024

## Client risk tolerance
Client risk tolerance is recorded on a 1-7 scale and represents the highest
fund risk rating permitted by the seed-data suitability rules.

## Risk bands
- 1-2: Conservative
- 3-4: Moderate
- 5-6: Aggressive
- 7: Very Aggressive

## Fund risk rating
Fund risk ratings are also recorded from 1 to 7. The classification considers
the fund's broad investment strategy and the principal market risks associated
with that strategy. The rating is a product classification, not a forecast of
future returns and not a guarantee of realised volatility.

## Suitability mapping
- Client risk 1-2: funds rated 1-2.
- Client risk 3-4: funds rated 1-4.
- Client risk 5-6: funds rated 1-6.
- Client risk 7: funds rated 1-7.

## Other suitability rules
Recommendations must also comply with:
- client-specific sector exclusions;
- maximum single-holding concentration;
- minimum ESG rating where specified;
- maximum ongoing charge where specified.

## Deterministic implementation
The mandate rules compare exact structured values against these rules.
The language model may explain a screening result but must never replace the
screening calculation.

## Suitability is not a buy recommendation
A fund passing these mechanical checks is not automatically suitable in every
respect. A suitability assessment may require financial circumstances,
capacity for loss, time horizon, knowledge and experience and other information
outside this synthetic dataset."""
    },

    17: {
        "id": 17,
        "title": "Meridian Investment Restriction Hierarchy and Interpretation Standard",
        "doc_type": "policy",
        "document_date": date(2024, 1, 3),
        "effective_date": date(2024, 1, 3),
        "as_of_date": date(2024, 1, 3),
        "fund_id": None,
        "client_id": None,
        "status": "active",
        "version": "1.0",
        "authority": "firm_policy",
        "scope": "firm",
        "text": """MERIDIAN ASSET MANAGEMENT
INVESTMENT RESTRICTION HIERARCHY
Effective 3 January 2024

## Purpose
This standard explains how the knowledge system should interpret overlapping
investment restrictions.

## Priority order
1.Applicable legal or regulatory requirements.
2.Firm-wide mandatory policy.
3.Client-specific contractual restrictions.
4.Fund-specific investment mandate.
5.Portfolio construction preferences and qualitative objectives.

## Stricter-rule principle
Where two applicable restrictions differ and both are valid, the stricter
applicable restriction should not be ignored merely because another document
is less restrictive.

## Client versus firm policy
A client mandate can impose additional restrictions. A client document should
not be interpreted as permitting conduct prohibited by a mandatory firm rule.

## Structured-data precedence
Where a current structured record conflicts with descriptive prose in a
document, exact compliance calculations must use the current structured
record. The document should be treated as qualitative or historical context
unless it is explicitly the authoritative source for the relevant rule.

## Temporal precedence
A newer active document supersedes an older document when both address the
same policy or mandate, unless the older document is explicitly preserved for
historical interpretation.

## LLM rule
The LLM must state when the retrieved evidence is insufficient to determine
which restriction applies. It must not invent a hierarchy or infer an
exception that is not documented."""
    },

    18: {
        "id": 18,
        "title": "Meridian Fund Risk and Exposure Reporting Methodology",
        "doc_type": "methodology",
        "document_date": date(2024, 1, 4),
        "effective_date": date(2024, 1, 4),
        "as_of_date": date(2024, 1, 4),
        "fund_id": None,
        "client_id": None,
        "status": "active",
        "version": "1.0",
        "authority": "investment_operations",
        "scope": "firm",
        "text": """MERIDIAN ASSET MANAGEMENT
FUND RISK AND EXPOSURE REPORTING METHODOLOGY
Effective 4 January 2024

## Reported holdings
Fund records contain selected top holdings. The percentage labelled
Percentage_of_fund_represented states how much of the fund those listed
holdings represent. It does not imply that unlisted holdings have zero
weight.

## Sector exposure
A sector total may only be described as a complete fund-level sector exposure
when a complete holdings dataset or an explicit aggregate exposure field is
available. Summing listed holdings can establish a minimum represented
exposure, not necessarily total exposure.

## Look-through portfolios
For a portfolio position with weight P and a fund holding with weight H, the
effective portfolio exposure is calculated as:

    P * H / 100

The mandate rules perform this arithmetic. The LLM should explain the
result rather than calculate it.

## Concentration
A single holding is compared directly with the client's maximum holding
percentage. Equality with the maximum is permitted under the current
screening convention.

## Fixed income
For bond funds, duration provides a measure of sensitivity to interest-rate
changes. Yield-to-maturity is a portfolio-level indicator and should not be
treated as a guaranteed future return.

## Data limitations
If the structured data does not provide a complete exposure, maturity,
duration, credit-quality or geographic breakdown, the knowledge system must
say that the requested figure is unavailable rather than infer it from the
top holdings."""
    },

    19: {
        "id": 19,
        "title": "Meridian Fee and Charges Disclosure Policy",
        "doc_type": "disclosure",
        "document_date": date(2023, 5, 20),
        "effective_date": date(2023, 5, 20),
        "as_of_date": date(2023, 5, 20),
        "fund_id": None,
        "client_id": None,
        "status": "active",
        "version": "1.0",
        "authority": "firm_policy",
        "scope": "firm",
        "text": """MERIDIAN ASSET MANAGEMENT
FEE AND CHARGES DISCLOSURE POLICY
Effective 20 May 2023

## Fund-level charges
For each managed fund, Meridian distinguishes:
- Ongoing Charge Figure: recurring management, administration and operational
  costs represented by the fund-level charge.
- Transaction costs: estimated costs of buying and selling holdings.
- Incidental costs: performance fees or other irregular charges where
  applicable.

## Service-level charges
Advisory and management services may have separate fees. A client agreement
can therefore contain an advisory fee that is additional to the fund's
ongoing charge.

## Interpretation
When comparing a fund against a client's maximum ongoing charge, use the
structured fund record's ongoing_charge_pct. Do not add a client advisory
fee to the fund OCF unless the question specifically asks for total client
cost.

## Disclosure principle
Fees should be presented clearly and updated when the applicable fee schedule
changes.

## Important limitation
This policy explains fee terminology and disclosure. It is not the
authoritative source for the current numerical fee of an individual fund;
the current structured fund record is used for deterministic screening."""
    },

    20: {
        "id": 20,
        "title": "Meridian Knowledge Base Definitions and Data Limitations",
        "doc_type": "glossary",
        "document_date": date(2024, 1, 5),
        "effective_date": date(2024, 1, 5),
        "as_of_date": date(2024, 1, 5),
        "fund_id": None,
        "client_id": None,
        "status": "active",
        "version": "1.0",
        "authority": "investment_operations",
        "scope": "firm",
        "text": """MERIDIAN KNOWLEDGE BASE
DEFINITIONS AND DATA LIMITATIONS
Effective 5 January 2024

## Risk tolerance
The maximum fund risk rating permitted by the current synthetic suitability
rules for a client.

## Risk rating
A 1-7 product risk classification assigned to a fund. It is not a guaranteed
measure of realised volatility.

## ESG rating
A-D sustainability classification. Unrated means no A-D rating is assigned.

## Ongoing charge
The fund-level recurring charge represented by ongoing_charge_pct in the
structured record.

## Benchmark
A reference index or benchmark used to contextualise fund performance. A
benchmark is not automatically a target portfolio or a suitability rule.

## Top holdings
The listed holdings in a fund record are selected reported positions, not
necessarily the entire portfolio.

## Look-through exposure
The effective exposure of a portfolio to an underlying holding or sector
after accounting for the portfolio's allocation to the fund.

## Client mandate
The documented investment restrictions and objectives applicable to a client.

## Screening result
A deterministic result produced from structured records. It is the source
of truth for the mechanical compliance checks implemented by the mandate rules.

## Historical commentary
A manager's explanation of conditions and decisions at a particular date.
Historical commentary must not be presented as current information without
an appropriate date caveat.

## Data limitation rule
The absence of information is not evidence of zero exposure, zero risk or
compliance. If the records and retrieved documents do not establish an
answer, the knowledge system should say that the evidence is insufficient."""
    },

    # -----------------------------------------------------------------------
    # FUND-LEVEL RISK / PERFORMANCE REPORTS
    # -----------------------------------------------------------------------
    21: {
        "id": 21,
        "title": "2024 Fund Risk and Positioning Review - Meridian Global Equity Growth",
        "doc_type": "risk_report",
        "document_date": date(2024, 12, 31),
        "effective_date": date(2024, 12, 31),
        "as_of_date": date(2024, 12, 31),
        "fund_id": 1,
        "client_id": None,
        "status": "active",
        "version": "1.0",
        "authority": "fund_management",
        "scope": "fund",
        "text": """MERIDIAN GLOBAL EQUITY GROWTH
2024 RISK AND POSITIONING REVIEW
As of 31 December 2024

## Principal active-risk themes
The fund's principal active-risk themes during 2024 were growth exposure,
technology concentration and the relative performance of U.S. and European
equities.

The manager considers technology and healthcare important sources of return
potential, while recognising that concentration in growth industries can
increase sensitivity to valuation changes and earnings expectations.

## Portfolio construction
The fund uses multiple positions rather than relying on a single company.
The structured holdings report should be used for exact current weights.
The listed positions represent only part of the fund.

## Risk interpretation
A risk rating of 5 places the fund in the aggressive band under Meridian's
suitability methodology. This classification should not be translated into a
specific expected return or volatility figure.

## Benchmark context
Performance should be discussed relative to the Meridian Global Equity Growth
Reference Index where benchmark-relative data is available. The current
knowledge base does not contain a complete numerical benchmark-return series,
so the system must not invent one."""
    },

    22: {
        "id": 22,
        "title": "2024 Fund Risk and Positioning Review - Meridian Emerging Markets Equity",
        "doc_type": "risk_report",
        "document_date": date(2024, 12, 31),
        "effective_date": date(2024, 12, 31),
        "as_of_date": date(2024, 12, 31),
        "fund_id": 2,
        "client_id": None,
        "status": "active",
        "version": "1.0",
        "authority": "fund_management",
        "scope": "fund",
        "text": """MERIDIAN EMERGING MARKETS EQUITY
2024 RISK AND POSITIONING REVIEW
As of 31 December 2024

## Principal risks
The fund's principal risk sources are emerging-market equity volatility,
currency movements, commodity exposure, political risk and differences in
market liquidity.

## Positioning
The reported portfolio contains technology, financials, materials, energy,
telecommunications, consumer and tobacco exposure. Exact weights must be
taken from the current structured record.

## ESG and exclusions
The reported 3% tobacco position is a material fact for mandate screening.
A client with a tobacco exclusion should therefore be checked against the
deterministic mandate rules rather than assessed by the language model.

## Historical context
The Q3 2023 manager commentary provides historical explanations for
commodity, currency and geopolitical weakness. It should not be treated as
a current market forecast."""
    },

    23: {
        "id": 23,
        "title": "2024 Fixed Income Risk Report - Meridian Global Government and Corporate Bond",
        "doc_type": "risk_report",
        "document_date": date(2024, 12, 31),
        "effective_date": date(2024, 12, 31),
        "as_of_date": date(2024, 12, 31),
        "fund_id": 4,
        "client_id": None,
        "status": "active",
        "version": "1.0",
        "authority": "investment_management",
        "scope": "fund",
        "text": """MERIDIAN GLOBAL GOVERNMENT AND CORPORATE BOND
2024 FIXED INCOME RISK REPORT
As of 31 December 2024

## Rate sensitivity
The structured record reports portfolio duration of 5.2 years. Duration is
an indicator of sensitivity to changes in interest rates; it is not a
guaranteed loss or return for a particular rate move.

## Income
The structured record reports a 4.1% yield-to-maturity. Yield-to-maturity is
a portfolio-level measure based on current holdings and assumptions. It is
not a promise that an investor will earn exactly 4.1%.

## Concentration
The reported top position is Government of Alderland at 12.0%. This is
relevant to clients with concentration limits.

## Credit and issuer risk
Corporate bonds introduce credit and spread risk in addition to general
interest-rate risk. Government holdings can introduce sovereign and currency
risk.

## Data limitation
The knowledge base does not contain a complete maturity ladder, credit-rating
distribution or currency breakdown. Those measures should not be inferred
from the listed top holdings."""
    },

    24: {
        "id": 24,
        "title": "2024 Thematic Risk Review - Meridian Active Thematic Equity",
        "doc_type": "risk_report",
        "document_date": date(2024, 12, 31),
        "effective_date": date(2024, 12, 31),
        "as_of_date": date(2024, 12, 31),
        "fund_id": 6,
        "client_id": None,
        "status": "active",
        "version": "1.0",
        "authority": "fund_management",
        "scope": "fund",
        "text": """MERIDIAN ACTIVE THEMATIC EQUITY
2024 THEMATIC RISK REVIEW
As of 31 December 2024

## Thematic concentration
The reported holdings are concentrated in technology and companies associated
with technology-enabled growth themes. This can make the fund more sensitive
to changes in valuation, adoption expectations and investor sentiment.

## Performance profile
The structured NAV series shows an increase in Q2 followed by declines in Q3
and Q4. The knowledge base does not contain a formal quarter-by-quarter
performance attribution report for the full year, so the system must not
invent specific causes for those movements.

## ESG
The fund is recorded as unrated. Unrated is a data classification and should
not be interpreted as an ESG score.

## Cost
The fund has a 2.25% ongoing charge in the structured record. Whether that
fee is acceptable depends on the client's mandate and the applicable
screening rule."""
    },

    25: {
        "id": 25,
        "title": "2024 Frontier Markets Risk Review - Meridian Frontier Markets",
        "doc_type": "risk_report",
        "document_date": date(2024, 12, 31),
        "effective_date": date(2024, 12, 31),
        "as_of_date": date(2024, 12, 31),
        "fund_id": 7,
        "client_id": None,
        "status": "active",
        "version": "1.0",
        "authority": "fund_management",
        "scope": "fund",
        "text": """MERIDIAN FRONTIER MARKETS
2024 FRONTIER MARKETS RISK REVIEW
As of 31 December 2024

## Risk classification
The fund has the highest risk rating in the structured seed data. Frontier
market exposure can involve elevated liquidity, currency, political,
regulatory and governance risks.

## Reported sector exposures
The listed holdings include fossil fuels, financials, telecommunications,
materials, gambling and weapons. These reported positions are particularly
relevant to client mandates containing ethical exclusions.

## Performance context
The structured NAV series shows a decline through Q3 followed by a partial
recovery in Q4. The knowledge base does not contain a detailed attribution
report for this fund, so a question asking exactly why those quarterly
movements occurred should be answered as insufficiently supported.

## Screening
The exact impact of the reported holdings, risk rating and ESG rating on a
client mandate must be determined using the mandate rules."""
    },
}


# Convenience list for indexing code that prefers iteration over dict values.
DOCUMENT_LIST = list(DOCUMENTS.values())
