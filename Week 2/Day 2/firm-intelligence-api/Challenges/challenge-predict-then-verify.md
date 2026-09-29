# Challenge: rank it yourself, then check the machine

**40 minutes. Laptops closed for the first half.**

You have built something that turns text into numbers and ranks
documents by how close those numbers sit together. Before you trust it, find out how well it
actually matches your own judgement.

---

## Part One: predict (laptops closed, 15 minutes)

Below are the eight documents already sitting in your index. Read them again, properly this
time, not skimming for code.

For each of the three questions, write down which document you think is the **best** match,
and one sentence on **why**. Do this before looking at anyone else's answers.

**The documents:**

| id | title |
|---|---|
| doc-001 | Harding & Voss - Market Position Note |
| doc-002 | Marchetti Ruiz - Compensation Review |
| doc-003 | Okonkwo Bell - Strategy Briefing |
| doc-004 | Sandoval Kerr - Risk and Compliance Summary |
| doc-005 | Lindqvist Partners - APAC Expansion Review |
| doc-006 | UK Market Commentary - Lateral Hiring |
| doc-007 | Jurisdiction Note - EU Practice Rights |
| doc-008 | Benchmarking Methodology |

*(Full text is in `documents.py` - go and actually read it again rather than working from
the titles alone.)*

**Question 1**
> Which firm works in energy and infrastructure?

My prediction: ______________
Why: ___________________________________________

**Question 2**
> Which firms operate in the United States?

My prediction: ______________
Why: ___________________________________________

**Question 3**
> Has any firm had a regulatory or compliance problem recently?

My prediction: ______________
Why: ___________________________________________

---

## Part Two: discuss (10 minutes)

Compare your three answers with the person next to you before opening a laptop. Where did
you agree? Where did you disagree, and why?

---

# PAUSE
### We will come back to this after we implement our endpoint




## Part Three: verify (10 minutes)

Laptops open. Run each of your three questions through the real endpoint:

```bash
curl -X POST http://127.0.0.1:8000/knowledge/search -H "Content-Type: application/json" \
  -d '{"question":"YOUR QUESTION HERE"}'
```

For each one, write down what the machine actually returned as its top result, and its
score.

**Question 1 - machine's top result:** ______________
**Did it match your prediction?** Y / N
knowledge.search("Which firm works in energy and infrastructure?", top_k=3)
[{'id': 'doc-003', 'title': 'Okonkwo Bell — Strategy Briefing', 'text': "Okonkwo Bell is a boutique with a deliberately narrow focus. The firm has built a reputation in energy and infrastructure work, particularly projects with a development finance element. It is not trying to be a full-service firm and has turned away work outside its core areas. Headcount has grown slowly and deliberately. The firm's leadership has been explicit that it does not intend to merge, and has declined at least two approaches in the past three years.", 'score': 0.4445349244383033}, {'id': 'doc-001', 'title': 'Harding & Voss — Market Position Note', 'text': 'Harding & Voss remains one of the stronger mid-tier performers in the UK market. Revenue growth has been steady rather than spectacular, and the firm has resisted the temptation to chase headline lateral hires. Its disputes practice is widely regarded as the strongest part of the business, particularly in commercial litigation and international arbitration. The corporate team is competent but has not won a significant mandate outside the UK in the last eighteen months. Partner retention is good. The firm does not operate in the United States and has no plans to open there.', 'score': 0.23587258414890355}, {'id': 'doc-004', 'title': 'Sandoval Kerr — Risk and Compliance Summary', 'text': "Sandoval Kerr has invested heavily in its conflicts and compliance function following a difficult period two years ago. The firm's matter intake process now requires sign-off from a dedicated risk partner for any engagement above a defined threshold. Professional indemnity arrangements were renegotiated at the last renewal. There are no outstanding regulatory matters. The firm reports no material claims in the current period.", 'score': 0.20053045608681558}]

**Question 2 - machine's top result:** ______________
**Did it match your prediction?** Y / N
 knowledge.search("Which firms operate in the United States?", top_k=3)
[{'id': 'doc-001', 'title': 'Harding & Voss — Market Position Note', 'text': 'Harding & Voss remains one of the stronger mid-tier performers in the UK market. Revenue growth has been steady rather than spectacular, and the firm has resisted the temptation to chase headline lateral hires. Its disputes practice is widely regarded as the strongest part of the business, particularly in commercial litigation and international arbitration. The corporate team is competent but has not won a significant mandate outside the UK in the last eighteen months. Partner retention is good. The firm does not operate in the United States and has no plans to open there.', 'score': 0.3331372763654285}, {'id': 'doc-007', 'title': 'Jurisdiction Note — EU Practice Rights', 'text': 'Firms operating across EU member states continue to navigate divergent requirements on practice rights and establishment. The position for UK-qualified lawyers has not returned to the pre-2021 arrangement. Firms with a registered EU presence are largely unaffected. Those servicing EU clients from London face more friction, particularly in regulated advisory work. Reference EUPR-14 sets out the current position per jurisdiction.', 'score': 0.2938649929635766}, {'id': 'doc-003', 'title': 'Okonkwo Bell — Strategy Briefing', 'text': "Okonkwo Bell is a boutique with a deliberately narrow focus. The firm has built a reputation in energy and infrastructure work, particularly projects with a development finance element. It is not trying to be a full-service firm and has turned away work outside its core areas. Headcount has grown slowly and deliberately. The firm's leadership has been explicit that it does not intend to merge, and has declined at least two approaches in the past three years.", 'score': 0.2794320907062965}]

**Question 3 - machine's top result:** ______________
**Did it match your prediction?** Y / N
knowledge.search("Has any firm had a regulatory or compliance problem recently?", top_k=3)
[{'id': 'doc-004', 'title': 'Sandoval Kerr — Risk and Compliance Summary', 'text': "Sandoval Kerr has invested heavily in its conflicts and compliance function following a difficult period two years ago. The firm's matter intake process now requires sign-off from a dedicated risk partner for any engagement above a defined threshold. Professional indemnity arrangements were renegotiated at the last renewal. There are no outstanding regulatory matters. The firm reports no material claims in the current period.", 'score': 0.4919565977836593}, {'id': 'doc-001', 'title': 'Harding & Voss — Market Position Note', 'text': 'Harding & Voss remains one of the stronger mid-tier performers in the UK market. Revenue growth has been steady rather than spectacular, and the firm has resisted the temptation to chase headline lateral hires. Its disputes practice is widely regarded as the strongest part of the business, particularly in commercial litigation and international arbitration. The corporate team is competent but has not won a significant mandate outside the UK in the last eighteen months. Partner retention is good. The firm does not operate in the United States and has no plans to open there.', 'score': 0.33142967173575705}, {'id': 'doc-006', 'title': 'UK Market Commentary — Lateral Hiring', 'text': 'Lateral partner hiring across the UK market slowed in the most recent period, reversing three years of aggressive recruitment. Firms that over-extended on guaranteed packages are now carrying underperforming partners they cannot easily exit. The firms that held their discipline are in a materially better position. Disputes practices continue to attract the most competitive offers, while transactional teams have seen offers flatten.', 'score': 0.3187299673991228}]

---

## If you finish early

Try these two, same process, no need to write it up formally, just notice what happens:

> What is matter LP-2291?

> What is the position on fixed-share partners?

---

## Keep this sheet

You will want it again this afternoon.
