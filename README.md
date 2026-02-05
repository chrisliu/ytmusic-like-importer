# YouTube Music Like Importer

Import songs from a YouTube Music playlist into your liked songs.

## Installation

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Authentication

```bash
python setup_browser.py
```

1. Open https://music.youtube.com in your browser and log in
2. Open DevTools (F12) > Network tab
3. Click "Home" or "Explore" in the left sidebar to trigger a `/browse` POST request
4. Click the `/browse` request and copy the `Authorization` and `Cookie` headers
5. Paste them into the script prompts

Credentials are valid for ~2 years unless you log out.

## Scripts

### import_likes.py

Import all songs from a playlist to Liked Music.

```bash
python import_likes.py [options]
```

Options:
- `--delay SECS` - Delay between requests (default: 1.0)
- `--batch-size N` - Verify every N songs (default: 25)
- `--max-retries N` - Max retries per song (default: 5)
- `--no-reverse` - Don't reverse playlist order (default: reverse for Spotify imports)

Features:
- Batch verification to confirm likes were saved
- Rollback on verification failure
- Duplicate detection in source playlist

### diff_playlists.py

Compare two playlists to find missing, extra, and duplicate songs.

```bash
python diff_playlists.py
```

### list_songs.py

List songs in a playlist.

```bash
python list_songs.py [options]
```

Options:
- `--head N` - Show first N songs
- `--tail N` - Show last N songs

### unlike_songs.py

Unlike all songs from a playlist.

```bash
python unlike_songs.py [options]
```

Options:
- `--delay SECS` - Delay between requests (default: 0.5)

## Dependencies

- [ytmusicapi](https://github.com/sigma67/ytmusicapi) - Unofficial YouTube Music API
- [rich](https://github.com/Textualize/rich) - Terminal formatting
