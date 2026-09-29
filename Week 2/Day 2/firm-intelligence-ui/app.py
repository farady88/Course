import httpx
import streamlit as st

API_BASE_URL = "http://127.0.0.1:8000"

st.title("Firm Intelligence")

st.header("Ask")

question = st.text_input("Ask a question about a firm, person, or the market")

if st.button("Ask"):
    if not question.strip():
        st.warning("Type a question first.")
    else:
        try:
            response = httpx.post(
                f"{API_BASE_URL}/agent/ask",
                json={"question": question},
                timeout=60,
            )
            response.raise_for_status()
            result = response.json()

            if result.get("completed"):
                st.write(result.get("answer", ""))
            else:
                st.warning(
                    "The agent did not finish before hitting its iteration limit."
                )

            st.caption(
                f"Tool calls made: {result.get('tool_calls_made', 'n/a')} | "
                f"Input tokens: {result.get('input_tokens', 'n/a')} | "
                f"Output tokens: {result.get('output_tokens', 'n/a')}"
            )

        except httpx.HTTPStatusError as e:
            detail = e.response.json().get("detail", e.response.text)
            if "iteration limit" in str(detail).lower():
                st.warning(
                    "The agent hit its iteration limit before it could answer."
                )
            else:
                st.error(f"Request failed ({e.response.status_code}): {detail}")

        except httpx.RequestError as e:
            st.error(f"Could not reach the API: {e}")

st.header("Search only")

search_query = st.text_input("Search the knowledge base (retrieval only, no generation)")

if st.button("Search"):
    if not search_query.strip():
        st.warning("Type a search query first.")
    else:
        try:
            response = httpx.post(
                f"{API_BASE_URL}/knowledge/search",
                json={"question": search_query},
                timeout=30,
            )
            response.raise_for_status()
            results = response.json().get("results", [])

            if not results:
                st.info("No results.")
            else:
                for r in results:
                    st.write(f"**{r['title']}** (score {r['score']:.3f})")

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 409:
                st.warning(
                    "The knowledge index has not been built yet. "
                    "Build it first, then search again."
                )
            else:
                detail = e.response.json().get("detail", e.response.text)
                st.error(f"Search failed ({e.response.status_code}): {detail}")

        except httpx.RequestError as e:
            st.error(f"Could not reach the API: {e}")

st.header("Streaming summary")

firm_id = st.number_input("Firm ID", min_value=1, step=1, value=1)

if st.button("Get summary"):
    try:
        with httpx.stream(
            "GET",
            f"{API_BASE_URL}/firms/{int(firm_id)}/summary/stream",
            timeout=60,
        ) as response:
            if response.status_code != 200:
                response.read()
                try:
                    detail = response.json().get("detail", response.text)
                except ValueError:
                    detail = response.text
                st.error(f"Summary failed ({response.status_code}): {detail}")
            else:
                placeholder = st.empty()
                summary_text = ""
                for chunk in response.iter_text():
                    summary_text += chunk
                    placeholder.markdown(summary_text)

    except httpx.RequestError as e:
        st.error(f"Could not reach the API: {e}")
