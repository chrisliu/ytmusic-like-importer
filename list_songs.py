import argparse
import os

from rich.console import Console
from rich.table import Table
from ytmusicapi import YTMusic

# Parse arguments
parser = argparse.ArgumentParser(
    description="List songs in a YouTube Music playlist"
)
group = parser.add_mutually_exclusive_group()
group.add_argument("--head", type=int, metavar="N", help="Show first N songs")
group.add_argument("--tail", type=int, metavar="N", help="Show last N songs")
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
        choice = console.input("\nEnter playlist number to view: ")
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

# Apply head/tail filter
if args.head:
    display_tracks = tracks[: args.head]
    title_suffix = f"first {args.head}"
elif args.tail:
    display_tracks = tracks[-args.tail :]
    title_suffix = f"last {args.tail}"
else:
    display_tracks = tracks
    title_suffix = "all"

# Display songs
songs_table = Table(
    title=f"{selected_playlist['title']} ({title_suffix} of {len(tracks)} songs)"
)
songs_table.add_column("#", style="dim")
songs_table.add_column("Title")
songs_table.add_column("Artist")

# Calculate starting index for display
start_idx = len(tracks) - len(display_tracks) + 1 if args.tail else 1

for i, track in enumerate(display_tracks, start_idx):
    title = track.get("title", "Unknown")
    artists = ", ".join(a["name"] for a in track.get("artists", []) if a)
    songs_table.add_row(str(i), title, artists)

console.print(songs_table)
