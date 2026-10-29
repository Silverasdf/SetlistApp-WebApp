import pandas as pd
from app.engine import normalize_songs, make_setlist, sort_sample_into_clusters, write_setlist_to_string, write_template_to_string

def sample():
    return pd.DataFrame([
        {"Song":"A", "Artist":"OG", "Key":"A", "Tuning":"E Standard", "Time":3, "Mood":9, "Active":True},
        {"Song":"B", "Artist":"Band", "Key":"A", "Tuning":"E Standard", "Time":4, "Mood":5, "Active":True},
        {"Song":"C", "Artist":"Band", "Key":"D", "Tuning":"Drop D", "Time":3, "Mood":8, "Active":True},
        {"Song":"D", "Artist":"Band", "Key":"Misc", "Tuning":"E Standard", "Time":4, "Mood":3, "Active":False},
    ])

def test_normalize_adds_defaults():
    out = normalize_songs(pd.DataFrame([{"Song":"A"}]))
    assert list(out.columns) == ["Song", "Artist", "Key", "Tuning", "Time", "Mood", "Active"]
    assert out.iloc[0]["Artist"] == "Unknown Artist"
    assert bool(out.iloc[0]["Active"])

def test_make_setlist_respects_time_and_active():
    out = make_setlist(sample(), 7, 1.2, 0.8, seed=2)
    assert out["Time"].sum() <= 7
    assert "D" not in out["Song"].tolist()

def test_include_is_selected_when_fits():
    out = make_setlist(sample(), 7, 1.2, 0.8, includes=["B"], seed=2)
    assert "B" in out["Song"].tolist()

def test_text_marks_matching_key_and_tuning():
    out = sample().iloc[:2]
    assert write_setlist_to_string(out) == "A -->\nB"

def test_cluster_handles_empty_input():
    assert sort_sample_into_clusters(sample().iloc[0:0], 2).empty


def test_template_contains_default_columns():
    assert write_template_to_string() == "Song,Artist,Key,Tuning,Time,Mood,Active\n"
