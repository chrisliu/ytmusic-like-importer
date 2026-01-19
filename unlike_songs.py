import argparse
import os
import time

from rich.console import Console
from rich.table import Table
from ytmusicapi import YTMusic

# Parse arguments
parser = argparse.ArgumentParser(
    description="Unlike songs from a YouTube Music playlist"
)
parser.add_argument(
    "--delay",
    type=float,
    default=0.5,
    help="Delay between requests in seconds (default: 0.5)",
)
args = parser.parse_args()

# Initialize YTMusic with browser auth
AUTH_FILE = "browser.json"

if not os.path.exists(AUTH_FILE):
    raise SystemExit(
        f"Missing {AUTH_FILE}. Run: ytmusicapi browser\n"
        "See: https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html"
    )

yt = YTMusic(AUTH_FILE)

# Fetch all playlists
playlists = yt.get_library_playlists(limit=None)

# Display with rich table
console = Console()
table = Table(title="Your Playlists")
table.add_column("#", style="dim")
table.add_column("Playlist Name")
table.add_column("Songs", justify="right")

for i, playlist in enumerate(playlists, 1):
    table.add_row(str(i), playlist["title"], str(playlist.get("count", "?")))

console.print(table)

# Prompt user to select a playlist
while True:
    try:
        choice = console.input("\nEnter playlist number to unlike songs from: ")
        playlist_num = int(choice)
        if 1 <= playlist_num <= len(playlists):
            break
        console.print(
            f"[red]Please enter a number between 1 and {len(playlists)}[/red]"
        )
    except ValueError:
        console.print("[red]Please enter a valid number[/red]")

selected_playlist = playlists[playlist_num - 1]
console.print(
    f"\nFetching songs from: [bold]{selected_playlist['title']}[/bold]\n"
)

# Fetch all playlist tracks
playlist_data = yt.get_playlist(selected_playlist["playlistId"], limit=None)
tracks = playlist_data.get("tracks", [])

if not tracks:
    raise SystemExit("[red]No tracks found in this playlist[/red]")

console.print(f"Total songs: [bold]{len(tracks)}[/bold]\n")

# Confirmation prompt (default to no)
console.print(
    f"[yellow]WARNING: This will unlike all {len(tracks)} songs from "
    f"'{selected_playlist['title']}'[/yellow]"
)
confirm = (
    console.input("\nAre you sure you want to continue? (y/N): ")
    .strip()
    .lower()
)

if confirm not in ("y", "yes"):
    console.print("[dim]Cancelled. No songs were unliked.[/dim]")
    raise SystemExit(0)

# Unlike all songs in reverse order
for i, track in enumerate(reversed(tracks), 1):
    title = track.get("title", "Unknown")
    artists = ", ".join(a["name"] for a in track.get("artists", []) if a)
    video_id = track.get("videoId")

    if not video_id:
        console.print(f"[yellow]Skipping {title} (no video ID)[/yellow]")
        continue

    console.print(
        f"[{i}/{len(tracks)}] Unliking: [bold]{title}[/bold] by {artists}"
    )
    yt.rate_song(video_id, "INDIFFERENT")
    time.sleep(args.delay)

console.print(f"\n[green]Done! Unliked {len(tracks)} songs.[/green]")
