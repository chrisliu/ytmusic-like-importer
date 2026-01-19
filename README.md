# YouTube Music Like Importer

Import songs from a YouTube Music playlist into your liked songs.

## Installation

```bash
source .venv/bin/activate
pip install -r requirements.txt
```

## Usage

### Step 1: Authenticate

Follow the [ytmusicapi browser setup guide](https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html):

1. Run: `ytmusicapi browser`
2. Open YouTube Music in your browser and copy the request headers when prompted
3. This creates a `browser.json` file with your credentials

### Step 2: Import Songs

```bash
python import_likes.py
```

The script will:
1. Fetch your playlists from YouTube Music
2. Display a menu to select a playlist
3. Add all songs from the selected playlist to your liked songs

## Dependencies

- [ytmusicapi](https://github.com/sigma67/ytmusicapi) - Unofficial YouTube Music API
- [rich](https://github.com/Textualize/rich) - Terminal formatting
