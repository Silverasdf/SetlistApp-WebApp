from __future__ import annotations
from io import BytesIO, StringIO
import re
import pandas as pd
from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel, Field
from .engine import normalize_songs, make_setlist, sort_sample_into_clusters, write_setlist_to_string, write_template_to_string
from .spotify import fetch_playlist_songs

app = FastAPI(title="SetlistApp API", version="0.1.0")
app.add_middleware(CORSMiddleware, allow_origin_regex=r"^https?://(localhost|127\.0\.0\.1|10\.\d+\.\d+\.\d+|172\.\d+\.\d+\.\d+|192\.168\.\d+\.\d+)(:\d+)?$", allow_credentials=False, allow_methods=["GET", "POST", "OPTIONS"], allow_headers=["*"])

class Song(BaseModel):
    Song: str = "Unknown Song"
    Artist: str = "Unknown Artist"
    Key: str = "Misc"
    Tuning: str = "E Standard"
    Time: float = Field(default=1, ge=0)
    Mood: float = Field(default=5, ge=0)
    Active: bool = True

class GenerateRequest(BaseModel):
    songs: list[Song]
    og_weight: float = Field(default=1.2, ge=0)
    mood_weight: float = Field(default=0.8, ge=0)
    set_time: float = Field(default=60, gt=0)
    transition_time: float | None = Field(default=None, ge=0)
    cluster_size: int = Field(default=2, ge=1, le=20)
    includes: list[str] = Field(default_factory=list)
    seed: int | None = None

class ExportRequest(BaseModel):
    songs: list[Song]

@app.get("/api/health")
def health(): return {"status": "ok"}

@app.post("/api/import/csv")
async def import_csv(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".csv"):
        raise HTTPException(400, "Upload a .csv file.")
    content = await file.read()
    if len(content) > 5 * 1024 * 1024: raise HTTPException(413, "CSV must be 5 MB or smaller.")
    try:
        frame = normalize_songs(pd.read_csv(BytesIO(content)))
    except Exception as exc:
        raise HTTPException(400, f"Could not read CSV: {exc}") from exc
    return {"songs": frame.to_dict(orient="records"), "count": len(frame)}

@app.post("/api/import/spotify")
def import_spotify(payload: dict):
    url = str(payload.get("url", "")).strip()
    token = str(payload.get("token") or "").strip()
    if not re.fullmatch(r"https?://open\.spotify\.com/playlist/[A-Za-z0-9]+(?:\?[^\s]*)?", url):
        raise HTTPException(400, "Enter a valid open.spotify.com playlist URL.")
    # Spotify's official playlist-items API requires an OAuth access token and only permits
    # access to playlists owned by, or collaborative with, the authorized user.
    # Do not scrape Spotify or imply this endpoint can import arbitrary public playlists.
    if not token:
        raise HTTPException(501, "Login-free import of arbitrary public Spotify playlists is not supported by Spotify's current official API. Upload a CSV instead. The import adapter is isolated so a compliant provider can be added later.")
    try:
        songs = fetch_playlist_songs(url, token)
    except Exception as exc:
        raise HTTPException(400, f"Could not import Spotify playlist: {exc}") from exc
    return {"songs": songs, "count": len(songs)}

@app.post("/api/generate")
def generate(req: GenerateRequest):
    if not req.songs: raise HTTPException(400, "Import or add at least one song first.")
    songs = normalize_songs(pd.DataFrame([s.model_dump() for s in req.songs]))
    transition = req.transition_time if req.transition_time is not None else req.set_time * 0.1
    target = req.set_time - transition
    if target <= 0: raise HTTPException(400, "Transition time must be shorter than set time.")
    try:
        sampled = make_setlist(songs, target, req.og_weight, req.mood_weight, req.includes, req.seed)
        ordered = sort_sample_into_clusters(sampled, req.cluster_size, req.seed)
    except Exception as exc:
        raise HTTPException(400, f"Could not generate setlist: {exc}") from exc
    return {"songs": ordered.to_dict(orient="records"), "text": write_setlist_to_string(ordered), "song_count": len(ordered), "song_time_minutes": round(float(ordered["Time"].sum()), 2), "target_time_minutes": round(target, 2)}

@app.post("/api/export/csv")
def export_csv(req: ExportRequest):
    if not req.songs: raise HTTPException(400, "There are no songs to export.")
    frame = normalize_songs(pd.DataFrame([s.model_dump() for s in req.songs]))
    data = frame.to_csv(index=False).encode("utf-8-sig")
    return StreamingResponse(BytesIO(data), media_type="text/csv; charset=utf-8", headers={"Content-Disposition": 'attachment; filename="setlist.csv"'})

@app.post("/api/export/txt")
def export_txt(req: ExportRequest):
    if not req.songs: raise HTTPException(400, "There are no songs to export.")
    frame = normalize_songs(pd.DataFrame([s.model_dump() for s in req.songs]))
    data = write_setlist_to_string(frame).encode("utf-8")
    return StreamingResponse(BytesIO(data), media_type="text/plain; charset=utf-8", headers={"Content-Disposition": 'attachment; filename="setlist.txt"'})

@app.get("/api/export/template")
def export_template():
    data = write_template_to_string().encode("utf-8-sig")
    return StreamingResponse(BytesIO(data), media_type="text/csv; charset=utf-8", headers={"Content-Disposition": 'attachment; filename="setlist_template.csv"'})
