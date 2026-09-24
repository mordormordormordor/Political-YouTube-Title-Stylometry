"""Pure-helper tests for adding channels (pipeline_titles.add_channels, creators --append,
run_all --incremental): no data, no network."""

import pandas as pd
import pytest

from pipeline_titles import run_all
from pipeline_titles.add_channels import add_to_list, normalize_creator
from pipeline_titles.creators import append_creators, build_creators
from pipeline_titles.ingest.fetch_video_metadata import read_creator_list_text


def test_normalize_creator_accepts_handles_and_urls_and_rejects_the_rest():
    assert normalize_creator("@SecretScholars") == "@SecretScholars"
    assert normalize_creator("SecretScholars") == "@SecretScholars"
    assert normalize_creator("https://www.youtube.com/@SecretScholars/videos") == "@SecretScholars"
    assert normalize_creator(" @SecretScholars/ ") == "@SecretScholars"
    assert normalize_creator("https://rumble.com/c/GGreenwald/videos?x=1") == "rumble.com/c/GGreenwald"
    assert normalize_creator("rumble.com/c/GGreenwald") == "rumble.com/c/GGreenwald"
    with pytest.raises(ValueError):
        normalize_creator("https://www.youtube.com/watch?v=abc")
    with pytest.raises(ValueError):
        normalize_creator("two words")


LIST = "# the list\n@AsmonTV   # caption corpus\n\n# ---------- Rumble ----------\nrumble.com/c/GGreenwald\n"


def test_add_to_list_appends_under_a_dated_comment_and_skips_creators_already_there():
    text, added, already = add_to_list(LIST, ["@SecretScholars", "@asmontv", "@SecretScholars", "rumble.com/c/New"], today="2026-09-24")
    assert added == ["@SecretScholars", "rumble.com/c/New"] and already == ["@asmontv"]
    assert read_creator_list_text(text) == ["@AsmonTV", "rumble.com/c/GGreenwald", "@SecretScholars", "rumble.com/c/New"]
    assert "# ---------- added 2026-09-24 (pipeline_titles.add_channels) ----------\n@SecretScholars\nrumble.com/c/New\n" in text
    assert text.startswith(LIST.rstrip("\n") + "\n")                       # the old text is untouched
    # a second run with the same creators changes nothing
    again, added2, already2 = add_to_list(text, ["@SecretScholars"], today="2026-09-25")
    assert again == text and added2 == [] and already2 == ["@SecretScholars"]


def _prepared_and_channels():
    rows = []
    for creator, n in (("@Old", 60), ("@New", 30)):
        for i in range(n):
            rows.append({"creator": creator, "genre": "videos" if i % 10 else "streams", "is_dup": False, "platform": "youtube"})
    prepared = pd.DataFrame(rows)
    channels = pd.DataFrame([{"creator": "@Old", "tab": "videos", "channel_name": "Old ", "channel_follower_count": 1000},
                             {"creator": "@New", "tab": "videos", "channel_name": "New Channel", "channel_follower_count": 658000}])
    return prepared, channels


def test_append_creators_adds_only_the_missing_rows_and_keeps_hand_corrections():
    prepared, channels = _prepared_and_channels()
    built = build_creators(prepared, channels, seed={"@Old": ("Old Org", False, "")})
    existing = built[built["creator"] == "@Old"].astype(str).copy()
    existing.loc[:, "organisation"] = "Corrected by hand"                     # a hand correction in the CSV
    existing.loc[:, "n_videos"] = "999"
    out, added = append_creators(existing, built, today="2026-09-24")
    assert added == ["@New"] and len(out) == 2 and list(out.columns) == list(existing.columns)
    old = out[out["creator"] == "@Old"].iloc[0]
    assert old["organisation"] == "Corrected by hand" and old["n_videos"] == "999"   # untouched
    new = out[out["creator"] == "@New"].iloc[0]
    assert new["channel_name"] == "New Channel" and new["organisation"] == "@New" and new["clipper"] == "False"
    assert new["subscribers"] == "658000" and new["n_videos"] == "27" and new["n_streams"] == "3" and new["low_n_videos"] == "True"
    assert new["note"].startswith("added 2026-09-24; organization defaulted")
    # nothing to add: the table comes back as it is
    same, none = append_creators(out, built)
    assert none == [] and same.equals(out)


def test_incremental_run_passes_each_stage_its_arguments(monkeypatch):
    calls = {}

    class Mod:
        def __init__(self, name):
            self.name = name

        def main(self, argv):
            calls[self.name] = argv
            return 0

    monkeypatch.setattr(run_all.importlib, "import_module", lambda name: Mod(name.rsplit(".", 1)[1]))
    assert run_all.main(["--incremental", "--from", "creators", "--skip", "leaning"]) == 0
    assert calls["creators"] == ["--append"] and calls["topics"] == ["--label-only"] and calls["llm_rate"] == ["--rekey"]
    assert calls["features"] == [] and "leaning" not in calls and "prepare" not in calls
    calls.clear()
    assert run_all.main(["--from", "report_data"]) == 0
    assert calls == {"report_data": [], "report": []}
