"""Tests for Google News scraping dataflow."""

from datetime import datetime, timedelta

import pytest
import requests

from tradingagents.dataflows.news.google_news import getNewsData


class _FakeResponse:
    def __init__(self, html: str):
        self.content = html.encode("utf-8")


def _build_result_html(has_next: bool = False) -> str:
    next_link = '<a id="pnnext" href="/next">Next</a>' if has_next else ""
    return f"""
    <html>
      <body>
        <div class="SoaBEf">
          <a href="https://example.com/a1"></a>
          <div class="MBeuO">News Title A1</div>
          <div class="GI74Re">Snippet A1</div>
          <div class="LfVVr">2 hours ago</div>
          <div class="NUnG9d"><span>Source A</span></div>
        </div>
        <div class="SoaBEf">
          <a href="https://example.com/a2"></a>
          <div class="MBeuO">News Title A2</div>
          <div class="GI74Re">Snippet A2</div>
          <div class="LfVVr">1 hour ago</div>
          <div class="NUnG9d"><span>Source B</span></div>
        </div>
        {next_link}
      </body>
    </html>
    """


def test_get_news_data_parses_multiple_pages_and_converts_dates(monkeypatch):
    """Should parse multi-page results and normalize yyyy-mm-dd inputs."""
    captured_urls = []
    pages = [
        _FakeResponse(_build_result_html(has_next=True)),
        _FakeResponse(_build_result_html(has_next=False)),
    ]

    def _fake_make_request(url, headers):
        captured_urls.append(url)
        return pages.pop(0)

    import tradingagents.dataflows.news.google_news as module

    monkeypatch.setattr(module, "make_request", _fake_make_request)

    result = getNewsData("test+query", "2026-03-10", "2026-03-13")

    assert len(result) == 4
    assert result[0]["title"] == "News Title A1"
    assert result[0]["source"] == "Source A"
    assert "cd_min:03/10/2026" in captured_urls[0]
    assert "cd_max:03/13/2026" in captured_urls[0]
    assert "start=10" in captured_urls[1]


def test_get_news_data_stops_after_repeated_timeout(monkeypatch):
    """Should stop gracefully after repeated timeout exceptions."""
    call_count = 0

    def _always_timeout(url, headers):
        nonlocal call_count
        call_count += 1
        raise requests.exceptions.Timeout("timeout")

    import tradingagents.dataflows.news.google_news as module

    monkeypatch.setattr(module, "make_request", _always_timeout)

    result = getNewsData("timeout+query", "2026-03-10", "2026-03-13")

    assert result == []
    assert call_count == 4


@pytest.mark.integration
def test_get_news_data_live_query_mei_yi_latest_24h():
    """Live integration test for the requested Chinese query."""
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    result = getNewsData("美伊战争24小时内最新进展", start_date, end_date)

    assert isinstance(result, list)
