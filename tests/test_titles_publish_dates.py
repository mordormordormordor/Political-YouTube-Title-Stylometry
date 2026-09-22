"""Pure-helper tests for the Data API publish-date fetch and its merge into the analysis table (no network)."""

from pathlib import Path

import pandas as pd

from pipeline_titles.common import apply_publish_dates, in_window
from pipeline_titles.ingest.fetch_publish_dates import chunks, exact_date, parse_env, parse_items, read_key


def test_chunks_are_fifty_wide_with_a_short_tail():
    ids = [f"v{i}" for i in range(123)]
    got = list(chunks(ids))
    assert [len(c) for c in got] == [50, 50, 23]
    assert got[0][0] == "v0" and got[-1][-1] == "v122"


def test_parse_env_and_read_key(tmp_path: Path):
    text = "# comment\nexport YOUTUBE_API_KEY='abc 123'\nOTHER=x=y\n\nbad line\n"
    assert parse_env(text) == {"YOUTUBE_API_KEY": "abc 123", "OTHER": "x=y"}
    env_file = tmp_path / ".env"
    env_file.write_text("YOUTUBE_API_KEY=fromfile\n")
    assert read_key("explicit", env={}, env_file=env_file) == "explicit"
    assert read_key(None, env={"YOUTUBE_API_KEY": "fromenv"}, env_file=env_file) == "fromenv"
    assert read_key(None, env={}, env_file=env_file) == "fromfile"
    assert read_key(None, env={}, env_file=tmp_path / "none") is None


def test_parse_items_records_every_id_asked_and_marks_the_missing():
    items = [
        {"id": "a", "snippet": {"publishedAt": "2026-03-17T14:00:00Z"}},
        {"id": "b", "snippet": {"publishedAt": "2026-03-01T01:00:00Z"}, "liveStreamingDetails": {"actualStartTime": "2026-03-02T23:30:00Z", "scheduledStartTime": "2026-03-02T23:00:00Z"}},
    ]
    rows = parse_items(items, ["a", "b", "c"], "2026-09-22T00:00:00Z")
    assert [r["video_id"] for r in rows] == ["a", "b", "c"]
    assert rows[0]["published_at"] == "2026-03-17T14:00:00Z" and rows[0]["actual_start"] is None and not rows[0]["missing"]
    assert rows[1]["actual_start"] == "2026-03-02T23:30:00Z" and rows[1]["scheduled_start"] == "2026-03-02T23:00:00Z"
    assert rows[2]["missing"] and rows[2]["published_at"] is None


def test_exact_date_prefers_a_streams_actual_start_and_reads_utc():
    assert exact_date({"published_at": "2026-03-17T23:30:00-05:00"}) == "2026-03-18"
    assert exact_date({"published_at": "2026-03-01T01:00:00Z", "actual_start": "2026-03-02T23:30:00Z"}) == "2026-03-02"
    assert exact_date({"published_at": None}) is None


def test_apply_publish_dates_overrides_only_matched_rows():
    df = pd.DataFrame({
        "video_id": ["a", "b", "r1"],
        "platform": ["youtube", "youtube", "rumble"],
        "published": ["2026-03-01", "2026-04-01", "2026-02-09"],
        "date_precision": ["approx", "approx", "exact"],
    })
    dates = pd.DataFrame({
        "video_id": ["a", "z"],
        "published_at": ["2026-03-17T14:00:00Z", "2026-01-01T00:00:00Z"],
        "actual_start": ["", ""],
        "scheduled_start": ["", ""],
        "published_exact": ["2026-03-17", "2026-01-01"],
    })
    out = apply_publish_dates(df, dates)
    assert out["published"].tolist() == ["2026-03-17", "2026-04-01", "2026-02-09"]
    assert out["date_precision"].tolist() == ["exact", "approx", "exact"]
    assert out["published_at"].tolist() == ["2026-03-17T14:00:00Z", "", ""]
    assert out["published_listed"].tolist() == ["2026-03-01", "2026-04-01", "2026-02-09"]
    assert out["month"].tolist() == ["2026-03", "2026-04", "2026-02"]


def test_in_window_keeps_the_dated_inside_and_the_undated():
    df = pd.DataFrame({"published": ["2025-12-31", "2026-01-01", "2026-09-14", "2026-09-15", ""]})
    assert in_window(df, "2026-01-01", "2026-09-14")["published"].tolist() == ["2026-01-01", "2026-09-14", ""]
