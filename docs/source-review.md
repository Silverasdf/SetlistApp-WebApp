# Source review before refactor

Reviewed the repository's current `src/main.py`, `src/gui.py`, `src/setlist_math.py`, `requirements.txt`, README, and the user-attached `format_csv.py`.

## Existing behavior to preserve

- CSV schema: `Song`, `Artist`, `Key`, `Tuning`, `Time`, `Mood`, `Active`.
- Set generation uses a target duration equal to set time minus transition time; transition defaults to 10% of set time.
- Songs with `Active == False` are excluded.
- Songs named in Includes are intended to be selected first if they fit.
- `Artist == 'OG'` uses the original-song weighting; other songs use `Mood ** mood_weight`.
- Songs are grouped into mood clusters; the legacy code tries to place high-mood songs near the beginning and end and shuffles middle clusters.
- Text export marks adjacent songs with matching non-`Misc` keys and matching tunings with `-->`; non-standard tunings are appended to the song name.

## Refactor observations

- `setlist_math.py` imports Tkinter and file-dialog dependencies even though the math module should be usable headlessly. The new engine has no GUI dependencies.
- The legacy `make_setlist` contains `if i not in df['Song']`, comparing a dataframe index with song-name values. This is not a valid check that an index exists; the new engine uses explicit row indices and song-name lookup for includes.
- The legacy cluster function assumes at least one cluster and can fail for an empty sample. The new engine returns an empty dataframe safely.
- The legacy UI persists active-state edits by mutating the original CSV. The web version edits data in browser memory and exports it explicitly instead of silently overwriting the user's source file.
- `format_csv.py` is a separate Tkinter script, not the PyQt application entry point. It normalizes columns but rewrites the selected CSV in place. The web version normalizes imported CSV data in memory.

## Scope and validation status

The source files were inspected through the public GitHub raw-file views. The runtime environment could not clone GitHub directly, and the only source file attached to this chat was `format_csv.py`; therefore this scaffold is a separate implementation package rather than a direct edit of a checked-out working tree. Backend tests pass locally with `python -m pytest -q`. Docker and frontend dependency installation have not been run in this environment.
