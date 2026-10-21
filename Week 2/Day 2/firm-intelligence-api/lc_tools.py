"""
Our search tool... written for LangChain
Retrievals is wrapped not rewritten: our tool will call knowledge_store.search, as our hand-built agent tool does.
"""

from langchain_core.tools import ToolException, tool
import knowledge_store as knowledge

@tool
def search_knowledge_base(query: str) -> str:
    "Search the firm intelligence knowledge base for docs relevant to a question about firm jurisdiction, compliance or market "

    try: 
        results = knowledge.search(query, top_k = 3)
    except RuntimeError as error:
        raise ToolException(f"Error: {error}")
    if not results:
        return "No relevant documents found"
    return "\n\n".join(
        f"[{r['id']}] {r['title']} (score {r['score']:.2f})\n{r['text']}" for r in results
    )