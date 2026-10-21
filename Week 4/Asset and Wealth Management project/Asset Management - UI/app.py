import os
from contextlib import contextmanager

import httpx
import pandas as pd
import streamlit as st

from helpers import fund_highlights, nav_frame, sector_exposure

API_BASE_URL = os.environ.get("API_BASE_URL", "http://127.0.0.1:8000")

st.set_page_config(page_title="Asset Management Intelligence", layout="wide")
st.title("Asset Management Intelligence")


@contextmanager
def api_errors(messages: dict[int, str] | None = None):
    "Show every API failure the same way (guide 10.5). `messages` overrides the text for a given status."
    try:
        yield
    except httpx.HTTPStatusError as e:
        status = e.response.status_code
        try:
            detail = e.response.json().get("detail", e.response.text)
        except ValueError:
            detail = e.response.text
        st.error((messages or {}).get(status) or f"Request failed ({status}): {detail}")
    except httpx.TimeoutException:
        st.error("The API took too long to respond. Try again.")
    except httpx.RequestError as e:
        st.error(f"Could not reach the API: {e}")


def call(method: str, path: str, timeout: float, messages: dict[int, str] | None = None, **kw):
    "One API request. Returns the response, or None after showing the error."
    with api_errors(messages):
        response = httpx.request(method, f"{API_BASE_URL}{path}", timeout=timeout, **kw)
        response.raise_for_status()
        return response
    return None


@st.cache_data(ttl=60)
def fetch_list(path: str) -> list[dict]:
    # Raises on failure, so a failed fetch is never cached.
    response = httpx.get(f"{API_BASE_URL}{path}", timeout=10)
    response.raise_for_status()
    return response.json()


def load(path: str) -> list[dict]:
    with api_errors():
        return fetch_list(path)
    return []


def tokens_caption(result: dict) -> str:
    return f"Input tokens: {result.get('input_tokens', 'n/a')} | Output tokens: {result.get('output_tokens', 'n/a')}"


def fund_label(f: dict) -> str:
    return f"{f['fund_id']}: {f['name']}"


# shortcut: a result vanishes if another widget triggers a rerun (no session_state), cache results if users complain
ask_tab, search_tab, summary_tab, compare_tab, fit_tab = st.tabs(
    ["Ask", "Search", "Summary", "Compare", "Client check"]
)

with ask_tab:
    mode = st.radio("Answer using", ["Agent (documents and mandate rules)", "Documents only"], horizontal=True)
    question = st.text_input("Ask a question", key="ask_question")
    if st.button("Ask"):
        if not question.strip():
            st.warning("Type a question first.")
        elif mode.startswith("Agent"):
            r = call("POST", "/agent/ask", 120, json={"question": question})
            if r:
                result = r.json()
                if not result.get("completed"):
                    st.warning("The agent ran out of steps before it could finish. Try a narrower question.")
                st.write(result["answer"])
                if result.get("stop_reason") == "max_tokens":
                    st.warning("The answer was cut off at the length limit and may be incomplete.")
                st.caption(f"Tool calls made: {result.get('tool_calls_made', 'n/a')} | {tokens_caption(result)}")
        else:
            r = call("POST", "/insights/ask", 60, json={"question": question})
            if r:
                result = r.json()
                if result["refused"]:
                    st.info(f"The system declined to answer. This is not an error: {result['reason']}")
                else:
                    st.write(result["answer"])
                    if not result["grounding"]["passed"]:
                        st.warning("Some sentences in this answer do not cite a document.")
                    for s in result["sources"]:
                        st.caption(f"Source [{s['id']}] {s['title']} (score {s['score']:.3f})")
                st.caption(tokens_caption(result))

with search_tab:
    query = st.text_input("Search the knowledge base (retrieval only, no generation)")
    top_k = st.slider("Results", 1, 8, 3)
    if st.button("Search"):
        if not query.strip():
            st.warning("Type a search query first.")
        else:
            r = call(
                "POST", "/knowledge/search", 30, json={"question": query, "top_k": top_k},
                messages={409: "The knowledge index has not been built. Build it with POST /knowledge/index on the API, then search again."},
            )
            if r:
                results = r.json()["results"]
                if not results:
                    st.info("No results.")
                for hit in results:
                    st.markdown(f"**{hit.get('title', hit['id'])}** ({hit['id']})")
                    st.caption(f"Score {hit['score']:.3f} | As of {hit.get('as_of_date', 'n/a')} | Status {hit.get('status', 'n/a')}")
                    st.write(hit["text"])

funds = load("/funds")
by_label = {fund_label(f): f for f in funds}

with summary_tab:
    label = st.selectbox("Fund", list(by_label), key="summary_fund")
    if st.button("Get summary") and label:
        with api_errors():
            with httpx.stream("GET", f"{API_BASE_URL}/funds/{by_label[label]['fund_id']}/summary/stream", timeout=60) as response:
                if response.status_code != 200:
                    response.read()
                    response.raise_for_status()
                st.write_stream(response.iter_text())

with compare_tab:
    chosen = [by_label[label] for label in st.multiselect("Choose two or more funds", list(by_label))]
    if len(chosen) < 2:
        st.info("Choose at least two funds to compare.")
    else:
        names = [f["name"] for f in chosen]
        st.dataframe(pd.DataFrame({
            "Strategy": [f["strategy"] for f in chosen],
            "Risk rating (1-7)": [f["risk_rating"] for f in chosen],
            "Ongoing charge %": [f["ongoing_charge_pct"] for f in chosen],
            "ESG rating": [f["esg_rating"] for f in chosen],
            "Top holdings": [", ".join(f"{h['name']} ({h['weight_pct']}%)" for h in f["holdings"][:3]) for f in chosen],
        }, index=names).astype(str).T, width="stretch")
        highlights = fund_highlights(chosen)
        st.success(f"Cheapest: {', '.join(highlights['cheapest'])}")
        st.warning(f"Highest risk: {', '.join(highlights['highest_risk'])}")
        left, right = st.columns(2)
        left.subheader("NAV per share by quarter")
        left.line_chart(nav_frame(chosen))
        right.subheader("Sector exposure (%)")
        right.bar_chart(sector_exposure(chosen))
        right.caption("Top holdings only, not the whole fund.")

with fit_tab:
    clients = {f"{c['client_id']}: {c['client_name']}": c for c in load("/clients")}
    fit_fund = st.selectbox("Fund", list(by_label), key="fit_fund")
    fit_client = st.selectbox("Client", list(clients))
    if st.button("Check fit") and fit_fund and fit_client:
        r = call("POST", "/insights/client-fit", 90, json={
            "fund_id": by_label[fit_fund]["fund_id"], "client_id": clients[fit_client]["client_id"]})
        if r:
            result = r.json()
            if result["breaches"]:
                st.subheader("Mandate breaches")
                st.dataframe(
                    pd.DataFrame(result["breaches"]).astype(str).style.map(lambda _: "color: red; font-weight: bold"),
                    width="stretch",
                )
            else:
                st.success("No breaches among the reported top holdings (this is not proof of zero exposure).")
            a = result["assessment"]
            (st.success if a["fits"] else st.error)(f"Fits the mandate: {a['fits']} | Recommended action: {a['recommended_action']} | Risk: {a['risk_alignment']}")
            st.write(a["rationale"])
            for s in a["strengths"]:
                st.markdown(f"- {s}")
            st.caption(tokens_caption(result))
