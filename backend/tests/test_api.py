from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health():
    response = client.get("/api/health")
    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_export_template_returns_default_columns():
    response = client.get("/api/export/template")
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/csv")
    assert 'attachment; filename="setlist_template.csv"' in response.headers["content-disposition"]
    assert "Song" in response.text
    assert "Artist" in response.text
    assert "Key" in response.text
    assert "Tuning" in response.text
    assert "Time" in response.text
    assert "Mood" in response.text
    assert "Active" in response.text


def test_import_csv_requires_file():
    response = client.post("/api/import/csv", data={})
    assert response.status_code == 422


def test_import_csv_normalizes_columns():
    response = client.post(
        "/api/import/csv",
        files={"file": ("songs.csv", b"Song,Artist,Key,Tuning,Time,Mood,Active\n\"New Song\",OG,A,E Standard,3,9,True\n", "text/csv")},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 1
    song = body["songs"][0]
    assert song["Song"] == "New Song"
    assert song["Artist"] == "OG"
    assert song["Time"] == 3.0
    assert song["Mood"] == 9.0
    assert song["Active"] is True


def test_import_csv_rejects_non_csv():
    response = client.post("/api/import/csv", files={"file": ("songs.txt", b"Song,Artist\nA,B\n", "text/plain")})
    assert response.status_code == 400


def test_generate_requires_songs():
    response = client.post("/api/generate", json={"songs": []})
    assert response.status_code == 400
    assert "at least one song" in response.json()["detail"]


def test_export_txt_requires_songs():
    response = client.post("/api/export/txt", json={"songs": []})
    assert response.status_code == 400
    assert "no songs" in response.json()["detail"]


def test_export_json_requires_songs():
    response = client.post("/api/export/json", json={"songs": []})
    assert response.status_code == 400
    assert "no songs" in response.json()["detail"]


def test_export_json_returns_song_records():
    response = client.post("/api/export/json", json={"songs": [{"Song": "New Song", "Artist": "OG", "Key": "A", "Tuning": "E Standard", "Time": 3, "Mood": 9, "Active": True}]})
    assert response.status_code == 200
    assert response.headers["content-type"].startswith("application/json")
    assert 'attachment; filename="setlist.json"' in response.headers["content-disposition"]
    body = response.json()
    assert body[0]["Song"] == "New Song"
    assert body[0]["Time"] == 3.0


def test_spotify_import_without_token_is_limited():
    response = client.post("/api/import/spotify", json={"url": "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M"})
    assert response.status_code == 501
    assert "not supported" in response.json()["detail"]


def test_spotify_import_rejects_invalid_url():
    response = client.post("/api/import/spotify", json={"url": "https://example.com/not-spotify", "token": "test-token"})
    assert response.status_code == 400
    assert "valid open.spotify.com" in response.json()["detail"]


def test_spotify_import_with_token_uses_provider(monkeypatch):
    def fake_fetch_songs(url, token):
        assert token == "test-token"
        return [{"Song": "Imported Song", "Artist": "OG", "Key": "Misc", "Tuning": "E Standard", "Time": 3.0, "Mood": 5.0, "Active": True}]

    def fake_fetch_info(url, token):
        assert token == "test-token"
        return {"name": "Band Favorites", "track_count": 1}

    monkeypatch.setattr("app.main.fetch_playlist_songs", fake_fetch_songs)
    monkeypatch.setattr("app.main.fetch_playlist_info", fake_fetch_info)
    response = client.post("/api/import/spotify", json={"url": "https://open.spotify.com/playlist/37i9dQZF1DXcBWIGoYBM5M", "token": "test-token"})
    assert response.status_code == 200
    body = response.json()
    assert body["count"] == 1
    assert body["songs"][0]["Song"] == "Imported Song"
    assert body["playlist_name"] == "Band Favorites"
    assert body["track_count"] == 1
