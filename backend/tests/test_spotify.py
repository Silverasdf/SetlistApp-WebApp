import httpx
import pytest
from app.spotify import fetch_playlist_songs, parse_playlist_id


def test_parse_playlist_id_extracts_id():
    assert parse_playlist_id("https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M?si=abc") == "37i9dQZF1DXcBWIGoYBM5M"


def test_parse_playlist_id_rejects_invalid_url():
    with pytest.raises(ValueError):
        parse_playlist_id("https://open.spotify.com/track/37i9dQZF1DXcBWIGoYBM5M")


def test_fetch_playlist_songs_maps_tracks():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"items": [
            {"track": {"name": "Song A", "artists": [{"name": "OG"}], "duration_ms": 180000}},
            {"track": {"name": "Song B", "artists": [{"name": "The Band"}], "duration_ms": 210000}},
        ]})

    songs = fetch_playlist_songs(
        "https://open.spotify.com/playlist/abc123",
        "token",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    assert len(songs) == 2
    assert songs[0]["Song"] == "Song A"
    assert songs[0]["Artist"] == "OG"
    assert songs[0]["Time"] == 3.0
    assert songs[1]["Song"] == "Song B"
    assert songs[1]["Artist"] == "The Band"
    assert songs[1]["Time"] == 3.5


def test_fetch_playlist_songs_maps_nested_item_shape():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(200, json={"items": [
            {"added_at": "2024-12-14T01:49:37Z", "is_local": False, "item": {"name": "All Hail Shadow", "artists": [{"name": "Spiritbox"}], "duration_ms": 210000}},
        ]})

    songs = fetch_playlist_songs(
        "https://open.spotify.com/playlist/abc123",
        "token",
        client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    assert len(songs) == 1
    assert songs[0]["Song"] == "All Hail Shadow"
    assert songs[0]["Artist"] == "Spiritbox"
    assert songs[0]["Time"] == 3.5


def test_fetch_playlist_songs_maps_404_to_error():
    def handler(request: httpx.Request) -> httpx.Response:
        return httpx.Response(404, json={"error": {"status": 404, "message": "Resource not found"}})

    with pytest.raises(ValueError, match="was not found or is not accessible"):
        fetch_playlist_songs(
            "https://open.spotify.com/playlist/missing",
            "token",
            client=httpx.Client(transport=httpx.MockTransport(handler)),
        )
