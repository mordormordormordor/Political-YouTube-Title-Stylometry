"""Pure-helper tests for pipeline_titles.ingest.fetch_video_metadata (no network)."""

import json

from pipeline_titles.ingest.fetch_video_metadata import (
    CSV_COLUMNS,
    channel_record,
    csv_row,
    flatten_entry,
    in_window,
    is_missing_tab_error,
    load_done,
    platform_of,
    read_creator_list,
    rumble_row,
    strip_comment,
    summarize_log,
    write_csv,
)


def test_strip_comment_handles_trailing_and_full_line_comments():
    assert strip_comment("@AsmonTV                 # caption corpus") == "@AsmonTV"
    assert strip_comment("# ---------- YouTube ----------") == ""
    assert strip_comment("   ") == ""
    assert strip_comment("https://rumble.com/c/GGreenwald   # Glenn Greenwald") == \
        "https://rumble.com/c/GGreenwald"
    # a '#' glued to the text is not a comment
    assert strip_comment("https://x.com/watch?v=abc#t=5") == "https://x.com/watch?v=abc#t=5"


def test_read_creator_list(tmp_path):
    p = tmp_path / "c.txt"
    p.write_text("# header\n@a  # note\n\n@b\nhttps://rumble.com/c/x # name\n", encoding="utf-8")
    assert read_creator_list(p) == ["@a", "@b", "https://rumble.com/c/x"]


def test_platform_of():
    assert platform_of("@hutch") == "youtube"
    assert platform_of("https://rumble.com/c/nickjfuentes") == "rumble"
    assert platform_of("HTTPS://RUMBLE.COM/c/x") == "rumble"


def test_flatten_entry_keeps_flat_fields_and_adds_provenance():
    entry = {"id": "abc", "title": "T", "url": "u", "duration": 61, "view_count": 5,
             "timestamp": 1767225600, "live_status": None, "thumbnails": [{"x": 1}],
             "_type": "url", "ie_key": "Youtube"}
    ch = {"channel": "Hutch", "channel_id": "UC1"}
    row = flatten_entry(entry, "@hutch", "videos", ch, "2026-09-14T00:00:00+00:00")
    assert row["video_id"] == "abc" and row["title"] == "T"
    assert row["published"] == "2026-01-01" and row["date_precision"] == "approx"
    assert row["creator"] == "@hutch" and row["platform"] == "youtube" and row["tab"] == "videos"
    assert row["channel_name"] == "Hutch" and row["channel_id"] == "UC1"
    assert "thumbnails" not in row and "_type" not in row and "ie_key" not in row


def test_flatten_entry_without_timestamp_is_undated():
    row = flatten_entry({"id": "x", "title": "t"}, "@c", "videos", {}, "now")
    assert row["published"] is None and row["date_precision"] is None


def test_rumble_row_uses_exact_dates():
    v = {"permalink_id": "v7dug5i", "id": 123, "title": "T", "url": "u",
         "upload_date": "2026-08-07", "duration": 100, "live": False}
    row = rumble_row(v, "https://rumble.com/c/nickjfuentes", {"channel": "nickjfuentes"}, "now")
    assert row["video_id"] == "v7dug5i" and row["published"] == "2026-08-07"
    assert row["date_precision"] == "exact" and row["platform"] == "rumble"


def test_in_window_bounds_and_drops_undated():
    assert in_window({"published": "2026-03-01"}, "2026-01-01", None)
    assert not in_window({"published": "2025-12-31"}, "2026-01-01", None)
    assert not in_window({"published": "2026-09-14"}, "2026-01-01", "2026-09-13")
    assert not in_window({"published": None}, "2026-01-01", None)
    assert in_window({"published": None}, None, None)


def test_channel_record_drops_bulk_keys():
    info = {"channel": "Hutch", "channel_id": "UC1", "channel_follower_count": 841000,
            "tags": ["a"], "thumbnails": [1], "entries": [], "description": "d"}
    rec = channel_record(info, "@hutch", "videos", "youtube", 12, "now")
    assert rec["channel_follower_count"] == 841000 and rec["videos_listed"] == 12
    assert "thumbnails" not in rec and "entries" not in rec


def test_load_done_only_counts_ok(tmp_path):
    p = tmp_path / "fetch_log.jsonl"
    p.write_text(json.dumps({"creator": "@a", "tab": "videos", "status": "ok"}) + "\n"
                 + json.dumps({"creator": "@b", "tab": "videos", "status": "error"}) + "\n"
                 + "not json\n", encoding="utf-8")
    assert load_done(p) == {("@a", "videos")}
    p.write_text(p.read_text() + json.dumps({"creator": "@c", "tab": "streams", "status": "no_tab"}) + "\n")
    assert load_done(p) == {("@a", "videos"), ("@c", "streams")}
    assert load_done(tmp_path / "missing.jsonl") == set()


def test_is_missing_tab_error():
    assert is_missing_tab_error("[youtube:tab] @AsmonTV: This channel does not have a streams tab")
    assert not is_missing_tab_error("HTTP Error 429: Too Many Requests")


def test_write_csv_dedupes_and_projects_columns(tmp_path):
    jl = tmp_path / "videos.jsonl"
    r1 = {"platform": "youtube", "tab": "videos", "video_id": "a", "title": "T1", "creator": "@c"}
    r2 = {"platform": "youtube", "tab": "videos", "video_id": "a", "title": "dup", "creator": "@c"}
    r3 = {"platform": "youtube", "tab": "streams", "video_id": "a", "title": "T2", "creator": "@c"}
    jl.write_text("\n".join(json.dumps(r) for r in (r1, r2, r3)) + "\n", encoding="utf-8")
    out = tmp_path / "videos.csv"
    assert write_csv(jl, out) == 2
    lines = out.read_text(encoding="utf-8").splitlines()
    assert lines[0].split(",") == CSV_COLUMNS
    assert len(lines) == 3
    assert csv_row(r1)[CSV_COLUMNS.index("title")] == "T1"


def test_summarize_log_uses_latest_status_per_job(tmp_path):
    p = tmp_path / "fetch_log.jsonl"
    recs = [
        {"creator": "@a", "tab": "videos", "status": "ok", "kept": 10},
        {"creator": "@a", "tab": "streams", "status": "error", "error": "boom"},
        {"creator": "@a", "tab": "streams", "status": "no_tab", "error": "no streams tab"},
        {"creator": "@b", "tab": "videos", "status": "error", "error": "gone"},
    ]
    p.write_text("\n".join(json.dumps(r) for r in recs) + "\n", encoding="utf-8")
    t = summarize_log(p)
    assert t["settled"] == 3 and t["ok"] == 1 and t["no_tab"] == 1 and t["error"] == 1
    assert t["videos_kept"] == 10
    assert t["errors"] == [("@b", "videos", "gone")]
    assert summarize_log(tmp_path / "missing.jsonl")["settled"] == 0
