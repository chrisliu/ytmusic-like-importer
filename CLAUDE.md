# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

YouTube Music Like Importer - imports songs from a YouTube Music playlist into liked songs. The goal is to provide a simple way to like all songs from a playlist using the `ytmusicapi` library.

## Commands

```bash
# Activate virtualenv
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run OAuth authentication (creates oauth.json)
ytmusicapi oauth

# Run the playlist importer
python import_likes.py
```

## Architecture

Single script:

**`import_likes.py`** - Playlist Import Script
- Fetches the user's playlists from YouTube Music
- Presents a CLI menu for the user to select a playlist
- Adds all songs from the selected playlist to the user's liked songs

OAuth authentication is handled by the `ytmusicapi oauth` CLI command (see [setup docs](https://ytmusicapi.readthedocs.io/en/stable/setup/oauth.html)).

## Dependencies

- `ytmusicapi` - YouTube Music API interactions
- `rich` - Terminal formatting for CLI menus

## Workflow

1. Activate the virtualenv
2. Run `ytmusicapi oauth` to authenticate with Google/YouTube Music
3. Run `python import_likes.py`
4. Select a playlist from the CLI menu
5. All songs from the playlist are added to your liked songs

## Commit Style

```
[tag] short description (<=80 chars)

- file1.py: what changed
- file2.py: what changed
```

Tags: `feat`, `fix`, `refactor`, `docs`, `chore`

No AI attribution.
