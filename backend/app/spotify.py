"""Spotify playlist import provider.

Uses Spotify's official Get Playlist Items and Get Playlist endpoints, which
require an OAuth access token. Anonymous access is not available, so token-less
callers are rejected by the API layer; this adapter performs the token-authorized
lookups.
"""
from __future__ import annotations
import re
import httpx

SPOTIFY_API_BASE = "https://api.spotify.com/v1"


def parse_playlist_id(url: str) -> str:
    match = re.search(r"playlist/([A-Za-z0-9]+)", url)
    if not match:
        raise ValueError("Enter a valid open.spotify.com playlist URL.")
    return match.group(1)


def _get_playlist(url: str, token: str, client: httpx.Client | None, endpoint: str) -> dict:
    """Fetch a Spotify playlist endpoint response and map failures to ValueError."""
    playlist_id = parse_playlist_id(url)
    http = client or httpx.Client(timeout=10.0)
    try:
        response = http.get(
            f"{SPOTIFY_API_BASE}/playlists/{playlist_id}{endpoint}",
            headers={"Authorization": f"Bearer {token}"},
        )
        response.raise_for_status()
        return response.json()
    except httpx.HTTPStatusError as exc:
        response = exc.response
        if response.status_code == 404:
            raise ValueError(f"Spotify playlist {playlist_id} was not found or is not accessible with this account/token.") from exc
        raise ValueError(f"Spotify playlist import failed with status {response.status_code}: {response.text}") from exc
    finally:
        if client is None:
            http.close()


def fetch_playlist_songs(url: str, token: str, client: httpx.Client | None = None) -> list[dict]:
    data = _get_playlist(url, token, client, "/items")
    items = data.get("items") or []
    songs: list[dict] = []
    for item in items:
        track_obj = item.get("track") or item.get("item") or item.get("video") or {}
        name = str(track_obj.get("name") or "").strip()
        artists = [str(artist.get("name")) for artist in (track_obj.get("artists") or []) if artist.get("name")]
        duration_ms = track_obj.get("duration_ms")
        duration_minutes = round(float(duration_ms or 0) / 60000.0, 1)
        songs.append({
            "Song": name or "Unknown Song",
            "Artist": ", ".join(artists) or "Unknown Artist",
            "Key": "Misc",
            "Tuning": "E Standard",
            "Time": duration_minutes if duration_minutes > 0 else 1.0,
            "Mood": 5.0,
            "Active": True,
        })
    return songs


def fetch_playlist_info(url: str, token: str, client: httpx.Client | None = None) -> dict:
    """Return playlist-level metadata such as the playlist name and track count."""
    data = _get_playlist(url, token, client, "")
    return {
        "name": str(data.get("name") or "Unknown Playlist"),
        "track_count": int(data.get("track_count") or 0),
    }
