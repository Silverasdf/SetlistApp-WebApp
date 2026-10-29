# SetlistApp

A local-first web app for building band setlists from a song catalog. The UI is Next.js + TypeScript; the setlist engine and file processing run in a Python FastAPI service. No account or database is required.

## Development note

This project was developed with AI coding assistance, with the goal of producing a clean, well-tested, production-shaped application that demonstrates backend, frontend, API, testing, and DevOps practices suitable for technical interviews.

## Features

- Import a CSV song catalog and normalize missing columns to defaults.
- Edit song metadata and active status in the browser.
- Configure set time, transition time, original-song weight, mood weight, and cluster size.
- Mark songs to include in the generated setlist.
- Export the catalog or generated setlist as CSV; export the setlist as TXT.
- Download a starter CSV template for a new catalog.
- Run locally with Docker Compose.

### Song CSV schema

| Column | Meaning | Default |
|---|---|---|
| `Song` | Song title | `Unknown Song` |
| `Artist` | Artist/band; `OG` is treated as an original | `Unknown Artist` |
| `Key` | Musical key | `Misc` |
| `Tuning` | Guitar tuning | `E Standard` |
| `Time` | Song duration in minutes | `1` |
| `Mood` | Numeric mood/energy weight | `5` |
| `Active` | Whether the song can be selected | `True` |

## Run with Docker

Requirements: Docker Desktop or Docker Engine with the Compose plugin.

```bash
git clone https://github.com/Silverasdf/SetlistApp.git
cd SetlistApp
docker compose up --build
```

Open <http://localhost:3000>. The API health endpoint is at <http://localhost:8000/api/health> and interactive API docs are at <http://localhost:8000/docs>.

Stop the app with `Ctrl+C`; run `docker compose down` to stop and remove the containers.

## Run without Docker

Backend:

```bash
cd backend
python -m venv .venv
# Windows: .venv\\Scripts\\activate
# macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000
```

Frontend in another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open <http://localhost:3000>. The frontend expects the API at `http://localhost:8000` by default.

## Self-hosting on a local machine with a domain

The stack is local-first and runs with Docker Compose:

```bash
docker compose up -d --build
```

Both services publish to `localhost` by default (frontend on `3000`, backend API on `8000`).

To host the app on a local machine behind a domain name, put a reverse proxy in front of the published ports and point the domain at the machine.

- Proxy `http://<domain>/` to the frontend (port `3000`).
- Proxy `http://<domain>/api/` to the backend API (port `8000`).

Example nginx server block:

```nginx
server {
    listen 80;
    server_name setlistapp.example.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
    }

    location /api/ {
        proxy_pass http://127.0.0.1:8000;
    }
}
```

Add an equivalent TLS server block (or use Certbot/Let's Encrypt) for `https://<domain>`.

Because the frontend calls the API at `NEXT_PUBLIC_API_BASE_URL` (default `http://localhost:8000`), rebuild the frontend image with a same-origin API base for production, e.g. `NEXT_PUBLIC_API_BASE_URL=https://<domain>`, so the browser talks to the domain directly. The backend serves the `/api/*` routes used by the frontend.

Until a domain is chosen, use <http://localhost:3000> with the API at <http://localhost:8000>.

## Spotify import status

The input accepts Spotify playlist URLs and an optional OAuth access token for the official import flow. Spotify's official Get Playlist Items endpoint requires OAuth and currently limits access to playlists owned by the authenticated user or playlists they collaborate on. Public visibility alone does not grant anonymous API access, so token-less imports are rejected with a clear message. This project does not scrape Spotify pages or bypass access controls.

With a valid access token, `POST /api/import/spotify` calls the Spotify provider and converts playlist tracks into song records (using defaults for key, tuning, and mood; duration comes from the track's `duration_ms`). For now, exporting or preparing the playlist as a CSV and importing that file is the way to get started without OAuth. The import route is isolated so a compliant provider can be added later.

References:
- [Spotify Get Playlist Items API](https://developer.spotify.com/documentation/web-api/reference/get-playlists-items)
- [Spotify Playlists concepts](https://developer.spotify.com/documentation/web-api/concepts/playlists)

## API

- `GET /api/health` — health check
- `GET /api/export/template` — download a CSV template with the default song columns
- `POST /api/import/csv` — multipart CSV import
- `POST /api/import/spotify` — reports current no-login API limitation
- `POST /api/generate` — generate a setlist from song records and settings
- `POST /api/export/txt` — download song records as a setlist text file
- `POST /api/export/csv` — download song records as CSV

## Development and CI

GitHub Actions runs Python tests and frontend type-check, lint, and production build on pushes and pull requests. Container deployment is intentionally not automated in this local-first scaffold; add image publishing and a deployment job after choosing a host.

## License

This repository retains the existing MIT license. See `LICENSE`.
