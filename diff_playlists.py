import os

from rich.console import Console
from rich.table import Table
from ytmusicapi import YTMusic

# Initialize YTMusic with browser auth
AUTH_FILE = "browser.json"

if not os.path.exists(AUTH_FILE):
    raise SystemExit(
        f"Missing {AUTH_FILE}. Run: ytmusicapi browser\n"
        "See: https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html"
    )

yt = YTMusic(AUTH_FILE)
console = Console()

# Fetch all playlists
playlists = yt.get_library_playlists(limit=None)

# Display with rich table
table = Table(title="Your Playlists")
table.add_column("#", style="dim")
table.add_column("Playlist Name")
table.add_column("Songs", justify="right")

for i, playlist in enumerate(playlists, 1):
    table.add_row(str(i), playlist["title"], str(playlist.get("count", "?")))

console.print(table)


def prompt_playlist(prompt_text):
    """Prompt user to select a playlist by number."""
    while True:
        try:
            choice = console.input(f"\n{prompt_text}: ")
            playlist_num = int(choice)
            if 1 <= playlist_num <= len(playlists):
                return playlists[playlist_num - 1]
            console.print(
                f"[red]Please enter a number between 1 and {len(playlists)}[/red]"
            )
        except ValueError:
            console.print("[red]Please enter a valid number[/red]")


def fetch_tracks(playlist):
    """Fetch all tracks from a playlist, handling Liked Music specially."""
    if playlist["title"] == "Liked Music":
        console.print(
            f"Fetching songs from: [bold]{playlist['title']}[/bold] (using get_liked_songs API)"
        )
        liked_data = yt.get_liked_songs(limit=None)
        return liked_data.get("tracks", [])
    else:
        console.print(f"Fetching songs from: [bold]{playlist['title']}[/bold]")
        playlist_data = yt.get_playlist(playlist["playlistId"], limit=None)
        return playlist_data.get("tracks", [])


# Prompt for source and target playlists
source_playlist = prompt_playlist("Enter SOURCE playlist number (original)")
target_playlist = prompt_playlist("Enter TARGET playlist number (to verify)")

console.print()

# Fetch tracks from both playlists
source_tracks = fetch_tracks(source_playlist)
target_tracks = fetch_tracks(target_playlist)

console.print(f"\nSource: [bold]{len(source_tracks)}[/bold] songs")
console.print(f"Target: [bold]{len(target_tracks)}[/bold] songs\n")

# Build lookup structures
# Source: dict mapping videoId -> list of (index, track) for showing position
source_by_id = {}
source_duplicates = []
for i, track in enumerate(source_tracks, 1):
    video_id = track.get("videoId")
    if video_id:
        if video_id in source_by_id:
            source_duplicates.append((i, track, source_by_id[video_id][0][0]))
        else:
            source_by_id[video_id] = []
        source_by_id[video_id].append((i, track))

# Target: set of videoIds for fast lookup
target_ids = {t.get("videoId") for t in target_tracks if t.get("videoId")}

# Find missing songs (in source but not in target)
missing = []
for video_id, occurrences in source_by_id.items():
    if video_id not in target_ids:
        index, track = occurrences[0]  # Use first occurrence
        missing.append((index, track))

# Sort by original index
missing.sort(key=lambda x: x[0])

# Find extra songs (in target but not in source)
source_ids = set(source_by_id.keys())
target_by_id = {}
for i, track in enumerate(target_tracks, 1):
    video_id = track.get("videoId")
    if video_id:
        target_by_id[video_id] = (i, track)

extras = []
for video_id, (index, track) in target_by_id.items():
    if video_id not in source_ids:
        extras.append((index, track))

extras.sort(key=lambda x: x[0])

# Display missing songs
if missing:
    missing_table = Table(title=f"Missing from Target ({len(missing)} songs)")
    missing_table.add_column("Source #", style="dim", justify="right")
    missing_table.add_column("Title")
    missing_table.add_column("Artist")
    missing_table.add_column("Video ID", style="dim")

    for index, track in missing:
        title = track.get("title", "Unknown")
        artists = ", ".join(a["name"] for a in track.get("artists", []) if a)
        video_id = track.get("videoId", "N/A")
        missing_table.add_row(str(index), title, artists, video_id)

    console.print(missing_table)
else:
    console.print(
        "[green]No missing songs! Target contains all source songs.[/green]"
    )

# Display extra songs
if extras:
    console.print()
    extras_table = Table(title=f"Extra in Target ({len(extras)} songs)")
    extras_table.add_column("Target #", style="dim", justify="right")
    extras_table.add_column("Title")
    extras_table.add_column("Artist")
    extras_table.add_column("Video ID", style="dim")

    for index, track in extras:
        title = track.get("title", "Unknown")
        artists = ", ".join(a["name"] for a in track.get("artists", []) if a)
        video_id = track.get("videoId", "N/A")
        extras_table.add_row(str(index), title, artists, video_id)

    console.print(extras_table)

# Display source duplicates
if source_duplicates:
    console.print()
    dup_table = Table(
        title=f"Duplicates in Source ({len(source_duplicates)} duplicates)"
    )
    dup_table.add_column("Position", style="dim", justify="right")
    dup_table.add_column("Title")
    dup_table.add_column("Artist")
    dup_table.add_column("First seen at", style="dim", justify="right")

    for index, track, first_index in source_duplicates:
        title = track.get("title", "Unknown")
        artists = ", ".join(a["name"] for a in track.get("artists", []) if a)
        dup_table.add_row(str(index), title, artists, str(first_index))

    console.print(dup_table)

# Summary
console.print("\n[bold]Summary[/bold]")
console.print(
    f"  Source: {len(source_tracks):,} songs ({len(source_by_id):,} unique)"
)
console.print(f"  Target: {len(target_tracks):,} songs")
console.print(f"  Missing: [red]{len(missing)}[/red] songs")
console.print(f"  Extras: [yellow]{len(extras)}[/yellow] songs")
if source_duplicates:
    console.print(
        f"  Duplicates in source: [cyan]{len(source_duplicates)}[/cyan]"
    )
