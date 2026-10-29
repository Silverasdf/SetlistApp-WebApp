"""Setlist generation logic separated from any UI or transport layer."""
from __future__ import annotations
import random
import pandas as pd

REQUIRED_COLUMNS = ["Song", "Artist", "Key", "Tuning", "Time", "Mood", "Active"]
DEFAULTS = {"Song": "Unknown Song", "Artist": "Unknown Artist", "Key": "Misc", "Tuning": "E Standard", "Time": 1.0, "Mood": 5.0, "Active": True}


def normalize_songs(frame: pd.DataFrame) -> pd.DataFrame:
    """Normalize uploaded CSVs to the legacy seven-column song schema."""
    df = frame.copy()
    for col, default in DEFAULTS.items():
        if col not in df.columns:
            df[col] = default
        df[col] = df[col].fillna(default)
    df = df[REQUIRED_COLUMNS]
    df["Song"] = df["Song"].astype(str).str.strip()
    df["Artist"] = df["Artist"].astype(str).str.strip()
    df["Key"] = df["Key"].astype(str).str.strip()
    df["Tuning"] = df["Tuning"].astype(str).str.strip()
    df["Time"] = pd.to_numeric(df["Time"], errors="coerce").fillna(1.0).clip(lower=0)
    df["Mood"] = pd.to_numeric(df["Mood"], errors="coerce").fillna(5.0).clip(lower=0)
    if df["Active"].dtype != bool:
        df["Active"] = df["Active"].map(_parse_bool).fillna(True)
    else:
        df["Active"] = df["Active"].fillna(True)
    return df.reset_index(drop=True)


def _parse_bool(value):
    if isinstance(value, bool): return value
    if value is None or pd.isna(value): return None
    value = str(value).strip().lower()
    if value in {"true", "1", "yes", "y", "active"}: return True
    if value in {"false", "0", "no", "n", "inactive"}: return False
    return None


def make_setlist(df: pd.DataFrame, target_time: float, og_weight: float, mood_weight: float, includes: list[str] | None = None, seed: int | None = None) -> pd.DataFrame:
    """Weighted sampling, retaining the original app's OG and mood weighting concepts."""
    df = normalize_songs(df)
    df = df[df["Active"]].copy().reset_index(drop=True)
    if target_time <= 0:
        return df.iloc[0:0].copy()
    rng = random.Random(seed)
    selected: list[int] = []
    selected_set: set[int] = set()
    total_time = 0.0
    includes = includes or []
    # Required songs are placed first, in the order supplied by the UI.
    for name in includes:
        matches = df.index[df["Song"] == name].tolist()
        for idx in matches:
            if idx in selected_set:
                continue
            duration = float(df.at[idx, "Time"])
            if total_time + duration <= target_time:
                selected.append(idx); selected_set.add(idx); total_time += duration
            break
    remaining = [i for i in df.index if i not in selected_set]
    while remaining and total_time < target_time:
        eligible = [i for i in remaining if total_time + float(df.at[i, "Time"]) <= target_time]
        if not eligible:
            break
        weights = []
        for i in eligible:
            mood = max(float(df.at[i, "Mood"]), 0.01)
            # Match the legacy implementation: OG rows use OG weight directly;
            # other rows use Mood ** mood_weight.
            if str(df.at[i, "Artist"]).strip().upper() == "OG":
                weight = max(float(og_weight), 0.0)
            else:
                weight = mood ** max(float(mood_weight), 0.0)
            weights.append(max(weight, 0.000001))
        chosen = rng.choices(eligible, weights=weights, k=1)[0]
        selected.append(chosen); selected_set.add(chosen); remaining.remove(chosen)
        total_time += float(df.at[chosen, "Time"])
    return df.loc[selected].reset_index(drop=True)


def sort_sample_into_clusters(sample: pd.DataFrame, cluster_size: int, seed: int | None = None) -> pd.DataFrame:
    """Group songs by mood and retain the legacy high-energy opening/closing preference."""
    if sample.empty: return sample.copy()
    if cluster_size < 1: raise ValueError("Cluster size must be at least 1.")
    rng = random.Random(seed)
    sorted_sample = sample.copy()
    sorted_sample["Mood"] = pd.to_numeric(sorted_sample["Mood"], errors="coerce").fillna(5)
    sorted_sample = sorted_sample.sort_values("Mood", ascending=False, kind="stable")
    clusters = [sorted_sample.iloc[i:i+cluster_size].copy() for i in range(0, len(sorted_sample), cluster_size)]
    if len(clusters) > 1 and clusters[0]["Mood"].max() < 7:
        for i in range(1, len(clusters)):
            if clusters[i]["Mood"].max() >= 8:
                clusters[0], clusters[i] = clusters[i], clusters[0]; break
    clusters[0] = clusters[0].sort_values("Mood", ascending=False, kind="stable")
    if len(clusters) > 2:
        middle = clusters[1:-1]; rng.shuffle(middle); clusters[1:-1] = middle
    if len(clusters) > 1 and clusters[-1]["Mood"].max() < 8:
        for i in range(len(clusters)-2, -1, -1):
            if clusters[i]["Mood"].max() >= 8:
                clusters[-1], clusters[i] = clusters[i], clusters[-1]; break
    if len(clusters) > 1:
        clusters[-1] = clusters[-1].sort_values("Mood", ascending=True, kind="stable")
    return pd.concat(clusters).reset_index(drop=True)


def write_setlist_to_string(setlist: pd.DataFrame) -> str:
    lines=[]
    for i, row in setlist.reset_index(drop=True).iterrows():
        name = str(row["Song"])
        if i < len(setlist)-1:
            nxt = setlist.iloc[i+1]
            if row["Key"] == nxt["Key"] and row["Tuning"] == nxt["Tuning"] and row["Key"] != "Misc":
                name += " -->"
        if row["Tuning"] != "E Standard": name += f" ({row['Tuning']})"
        lines.append(name)
    return "\n".join(lines)


def write_template_to_string() -> str:
    """Return the default CSV header row for a new song catalog."""
    return pd.DataFrame(columns=REQUIRED_COLUMNS).to_csv(index=False)
