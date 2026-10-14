**Hybrid Retrieval Briefing: Azure AI Search — Team D**

**##How it does hybrid search**

Azure AI Search runs keyword and vector searches in parallel within a single request. It combines their results using Reciprocal Rank Fusion (RRF), which uses rank positions rather than original scores. An optional semantic ranker then reranks the merged results to improve relevance.

Source: [Microsoft Learn — Hybrid search overview](https://learn.microsoft.com/en-us/azure/search/hybrid-search-overview)

**##Fusion and its defaults**

- **Method:** Azure uses RRF. It combines results based on their positions in each search list.
- **Defaults:**
  - **Text results:** By default, up to 1,000 keyword results can be considered for merging.
  - **Vector results:** The k setting controls how many vector results are considered. Microsoft recommends 50 when using the semantic ranker.
  - **Final results:** Azure returns up to 50 results by default. The top setting changes this number.
- **Weighting:** The default vector weight is 1.0. Increasing it gives vector results more influence. Decreasing it gives them less influence.

Sources: [RRF scoring](https://learn.microsoft.com/en-us/azure/search/hybrid-search-ranking) | [Hybrid query settings](https://learn.microsoft.com/en-us/azure/search/hybrid-search-how-to-query) | [Hybrid overview](https://learn.microsoft.com/en-us/azure/search/hybrid-search-overview)

**##The keyword side**

Azure AI Search uses BM25 to rank keyword search results. It uses an inverted index to find documents containing the search terms. This complements vector search, which finds documents with similar meaning.

Source: [Microsoft Learn — Hybrid search overview](https://learn.microsoft.com/en-us/azure/search/hybrid-search-overview)

**##One catch**

1. The optional semantic ranker can add extra cost. It has a monthly free allowance. After this runs out, a paid plan is needed to continue using semantic ranking.

**Source:** [Microsoft Learn — Semantic ranker billing](https://learn.microsoft.com/en-us/azure/search/semantic-how-to-enable-disable)

1. Large result lists and semantic reranking can make searches slower. We should test both response time and result quality.

**Source:** [Microsoft Learn — Create a hybrid query](https://learn.microsoft.com/en-us/azure/search/hybrid-search-how-to-query)

**##Evidence that hybrid helps**

Microsoft's 2023 test on customer datasets used NDCG@3, a measure of how relevant and well ordered the top three results are. Vector-only search scored 43.8, while hybrid scored 48.4—a gain of 4.6 points. Hybrid with semantic ranking scored 60.1. Microsoft ran this test on its own product, so we should also test our app.

| **Search method**        | **Quality score** |
| ------------------------ | ----------------- |
| Vector only              | 43.8              |
| Hybrid                   | 48.4              |
| Hybrid + semantic ranker | 60.1              |

Source: [Microsoft benchmark, Table 1](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/azure-ai-search-outperforming-vector-search-with-hybrid-retrieval-and-reranking/3929167)

**##Core Questions:**

**1\. Rank or score?**

- **Rank-based fusion**, such as RRF, uses each document's position in the search lists. **Gain:** It combines lists easily, even when their scores use different scales. **Throws away:** Original scores and the size of the gap between strong and weak matches.
- **Score-based fusion** puts scores on a common scale, then combines them. **Gain:** It keeps information about how strong each match is. **Throws away:** The original score scale. Rescaling can also change the gaps between scores.

Source: [Weaviate — Hybrid search](https://docs.weaviate.io/weaviate/concepts/search/hybrid-search)

**2\. Does hybrid help?**

- Yes, in Microsoft's 2023 test on customer datasets. Vector-only search scored **43.8**, while hybrid search scored **48.4**, a gain of **4.6 points**.

The metric was **NDCG@3**, which measures the relevance and order of the top three results. Microsoft tested its own product, so this is vendor evidence. We should test our app before expecting the same improvement.

Source: [Microsoft benchmark — Table 1](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/azure-ai-search-outperforming-vector-search-with-hybrid-retrieval-and-reranking/3929167)

- Microsoft's 2023 test on **BEIR**, a public collection of search datasets, found:

**Keyword-only:** 40.6, **Vector-only:** 45.0, **Hybrid:** 48.4

| **Search method** | **NDCG@10 score** |
| ----------------- | ----------------- |
| Keyword only      | 40.6              |
| Vector only       | 45.0              |
| Hybrid            | 48.4              |

The metric was **NDCG@10**, which measures the relevance and order of the top 10 results. Hybrid improved the score by **3.4 points over vector-only** and **7.8 points over keyword-only**.

Microsoft ran the test on its own product, so it is vendor evidence. We should test our app to check whether it gets similar benefits.

Source: [Microsoft benchmark — Table 1](https://techcommunity.microsoft.com/blog/azure-ai-foundry-blog/azure-ai-search-outperforming-vector-search-with-hybrid-retrieval-and-reranking/3929167)

**3\. Where does the keyword half come from?**

Search systems can use traditional BM25 or a learned sparse model.

- **BM25 example:** Azure AI Search finds matching words through an inverted index and ranks documents using BM25.
- **Learned sparse example:** Elasticsearch offers ELSER, a trained model that gives terms importance scores and adds related terms. This helps find relevant documents even when the wording differs.

Sources: [Azure hybrid search](https://learn.microsoft.com/en-us/azure/search/hybrid-search-overview) | [Elastic sparse search](https://www.elastic.co/docs/solutions/search/vector/sparse-vector)

**##Advice for our app**

We recommend testing hybrid search. Keep the existing vector search, add BM25 keyword search, and combine their results using RRF. Keyword search may help find exact codes such as LP-3307, while vector search can still find similar meanings.

Compare this with our current search using the same questions. Check whether the correct chunk appears in the top three results. Add semantic reranking only if testing shows further improvement.

Source: [Microsoft Learn — Hybrid search overview](https://learn.microsoft.com/en-us/azure/search/hybrid-search-overview)

**\## Open questions**

- Will keyword search find the correct chunk for LP-3307 in our app?
- What vector weight gives the best results for our questions?
- Does semantic reranking improve results enough to justify its extra cost?
- How should we change our current refusal rule? RRF scores are different from cosine similarity scores, so we cannot reuse the 0.45 threshold directly.
- Could score-based fusion be a better option for our app? How would you know?
- Would our Relevance floor shift again after utilizing RRF?

Source for score differences: [Microsoft Learn — RRF scoring](https://learn.microsoft.com/en-us/azure/search/hybrid-search-ranking)