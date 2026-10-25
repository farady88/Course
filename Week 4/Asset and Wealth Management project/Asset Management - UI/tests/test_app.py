import os
import sys

import httpx
import pytest
import streamlit as st
from streamlit.testing.v1 import AppTest

UI_DIR = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, UI_DIR)

FUND = {
    "fund_id": 1, "name": "Fund A", "strategy": "equity", "risk_rating": 5, "ongoing_charge_pct": 0.5, "esg_rating": "B",
    "holdings": [{"name": "x", "sector": "technology", "weight_pct": 6.0}],
    "NAV_per_share": [{"quarter": "Q1", "nav": 1.0}],
}
CLIENT = {"client_id": 1, "client_name": "Client One"}
HIT = {"id": "doc-01", "title": "Fund A mandate", "score": 0.612, "as_of_date": "2024-12-31", "status": "active", "text": "Body"}


def respond(status, body):
    return httpx.Response(status, json=body, request=httpx.Request("GET", "http://api"))


@pytest.fixture
def api(monkeypatch):
    "Fake the API. `routes` maps (method, path) to (status, json body); tests override entries."
    routes = {
        ("GET", "/funds"): (200, [FUND]),
        ("GET", "/clients"): (200, [CLIENT]),
        ("GET", "/portfolios"): (200, [{"portfolio_id": 1, "positions": [{"fund_id": 1, "weight_pct": 50.0}]}]),
        ("POST", "/knowledge/search"): (200, {"results": [HIT]}),
    }

    def request(method, url, timeout=None, **kw):
        status, body = routes[(method, url.replace("http://127.0.0.1:8000", ""))]
        return respond(status, body)

    monkeypatch.setattr(httpx, "request", request)
    monkeypatch.setattr(httpx, "get", lambda url, timeout=None: request("GET", url))
    return routes


def run_app():
    st.cache_data.clear()  # fetch_list caches fund and client lists across tests
    at = AppTest.from_file(os.path.join(UI_DIR, "app.py"), default_timeout=30).run()
    assert not at.exception
    return at


def click(at, label):
    next(b for b in at.button if b.label == label).click().run()
    return at


def test_features_are_five_tabs_not_one_long_page(api):
    assert [t.label for t in run_app().tabs] == ["Ask", "Search", "Summary", "Compare", "Client check"]


def test_search_lists_score_date_and_status(api):
    at = run_app()
    at.text_input[1].set_value("tobacco")
    click(at, "Search")
    assert any("0.612" in c.value and "2024-12-31" in c.value and "active" in c.value for c in at.caption)


def test_search_409_says_the_index_is_not_built(api):
    api[("POST", "/knowledge/search")] = (409, {"detail": "empty"})
    at = run_app()
    at.text_input[1].set_value("tobacco")
    click(at, "Search")
    assert "index has not been built" in at.error[0].value


def test_agent_that_ran_out_of_steps_gets_a_warning(api):
    api[("POST", "/agent/ask")] = (200, {"answer": "Agent stopped.", "completed": False, "tool_calls_made": 5,
                                         "input_tokens": 1, "output_tokens": 1, "stop_reason": "max_iterations"})
    at = run_app()
    at.text_input[0].set_value("a question")
    click(at, "Ask")
    assert "ran out of steps" in at.warning[0].value


def test_refusal_is_an_info_message_not_an_error(api):
    api[("POST", "/insights/ask")] = (200, {"answer": None, "refused": True, "reason": "No relevant document found.", "sources": []})
    at = run_app()
    at.radio[0].set_value("Documents only")
    at.text_input[0].set_value("something unrelated")
    click(at, "Ask")
    assert "declined" in at.info[0].value and not at.error


@pytest.mark.parametrize("button,path", [
    ("Get fund summary", "/funds/1/summary/stream"),
    ("Get portfolio summary", "/portfolios/1/summary/stream"),
])
def test_summary_streams_the_update_from_the_matching_endpoint(api, monkeypatch, button, path):
    urls = []

    class Streamed:
        status_code = 200

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

        def iter_text(self):
            yield from ["A plain ", "update."]

    monkeypatch.setattr(httpx, "stream", lambda method, url, timeout=None: urls.append(url) or Streamed())
    at = click(run_app(), button)
    assert not at.exception
    assert urls == [f"http://127.0.0.1:8000{path}"]
    assert any("A plain update." in m.value for m in at.markdown)


def test_compare_needs_two_funds_then_shows_highlights_and_charts(api):
    api[("GET", "/funds")] = (200, [FUND, {**FUND, "fund_id": 2, "name": "Fund B", "risk_rating": 2, "ongoing_charge_pct": 1.2}])
    at = run_app()
    assert "at least two" in at.info[0].value
    at.multiselect[0].set_value(["1: Fund A", "2: Fund B"]).run()
    assert not at.exception
    assert "Fund A" in at.success[0].value and "Fund A" in at.warning[0].value  # cheapest and highest risk
    assert len(at.dataframe) == 1


def test_client_check_shows_breaches_and_assessment(api):
    breach = {"rule": "excluded_sector", "actual": {"tobacco": 3.0}, "limit": ["tobacco"], "detail": "3% tobacco"}
    assessment = {"fits": False, "risk_alignment": "aligned", "breaches": [], "strengths": ["Low fee"],
                  "recommended_action": "review", "rationale": "Tobacco exposure."}
    api[("POST", "/insights/client-fit")] = (200, {"fund_id": 1, "client_id": 1, "breaches": [breach],
                                                   "assessment": assessment, "input_tokens": 5, "output_tokens": 6})
    at = run_app()
    click(at, "Check fit")
    assert not at.exception
    assert "Fits the mandate: False" in at.error[0].value
    assert len(at.dataframe) == 1
    assert any("Tobacco exposure." in m.value for m in at.markdown)
