import argparse
import os
import time

from rich.console import Console
from rich.table import Table
from ytmusicapi import LikeStatus, YTMusic

# Parse CLI arguments
parser = argparse.ArgumentParser(
    description="Import songs from a YouTube Music playlist to Liked Music"
)
parser.add_argument(
    "--delay",
    type=float,
    default=1.0,
    help="Delay between requests (default: 1.0s)",
)
parser.add_argument(
    "--batch-size",
    type=int,
    default=25,
    help="Verify every N songs (default: 25)",
)
parser.add_argument(
    "--max-retries",
    type=int,
    default=5,
    help="Max retries per song (default: 5)",
)
parser.add_argument(
    "--no-reverse",
    action="store_true",
    help="Don't reverse playlist order (default: reverse for Spotify imports)",
)
args = parser.parse_args()

# Initialize YTMusic with browser auth (more reliable than OAuth)
AUTH_FILE = "browser.json"

if not os.path.exists(AUTH_FILE):
    raise SystemExit(
        f"Missing {AUTH_FILE}. Run: ytmusicapi browser\n"
        "See: https://ytmusicapi.readthedocs.io/en/stable/setup/browser.html"
    )

yt = YTMusic(AUTH_FILE)
console = Console()


def get_liked_playlist_id(yt):
    """Find the Liked Music playlist by name."""
    playlists = yt.get_library_playlists(limit=None)
    liked = next((p for p in playlists if p["title"] == "Liked Music"), None)
    return liked["playlistId"] if liked else None


def verify_likes(yt, expected_tracks, start_idx, count):
    """Verify songs were added to Liked Music.

    Returns the index of the first song NOT found in Liked Music,
    or None if all songs were verified successfully.
    """
    liked_id = get_liked_playlist_id(yt)
    if not liked_id:
        return (
            start_idx  # Liked Music playlist doesn't exist = nothing was added
        )

    liked_data = yt.get_playlist(liked_id, limit=count * 2)
    liked_video_ids = {t.get("videoId") for t in liked_data.get("tracks", [])}

    # Check each song in order and return first missing one
    for idx in range(start_idx, start_idx + count):
        video_id = expected_tracks[idx].get("videoId")
        if video_id and video_id not in liked_video_ids:
            return idx

    return None  # All verified


def unlike_batch_with_verification(
    yt, tracks, start_idx, count, delay, console
):
    """Unlike a batch of songs and verify they were removed."""
    batch = tracks[start_idx : start_idx + count]

    while True:
        # Unlike all songs in batch
        for track in batch:
            video_id = track.get("videoId")
            if video_id:
                yt.rate_song(video_id, LikeStatus.INDIFFERENT)
                time.sleep(delay)

        # Verify songs were removed from Liked Music
        liked_id = get_liked_playlist_id(yt)
        if not liked_id:
            console.print(
                "[green]Rollback verified (Liked Music empty)[/green]"
            )
            return

        liked_data = yt.get_playlist(liked_id, limit=count * 2)
        liked_video_ids = {
            t.get("videoId") for t in liked_data.get("tracks", [])
        }
        batch_video_ids = {t.get("videoId") for t in batch if t.get("videoId")}

        # Check none of the batch songs are in liked anymore
        if not batch_video_ids.intersection(liked_video_ids):
            console.print("[green]Rollback verified[/green]")
            return

        console.print(
            "[yellow]Rollback verification failed, retrying unlike...[/yellow]"
        )
        time.sleep(delay)


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

# Prompt user to select a playlist
while True:
    try:
        choice = console.input("\nEnter playlist number to import from: ")
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

# Reverse tracks so oldest songs are liked first (appear at bottom of Liked Music)
# This is the default behavior for Spotify imports
if not args.no_reverse:
    tracks = list(reversed(tracks))

# Detect duplicates
seen_ids = {}
duplicates = []
for i, track in enumerate(tracks, 1):
    video_id = track.get("videoId")
    if video_id:
        if video_id in seen_ids:
            duplicates.append((i, track, seen_ids[video_id]))
        else:
            seen_ids[video_id] = i

unique_count = len(seen_ids)

if duplicates:
    console.print(
        f"Found [bold]{len(tracks)}[/bold] songs ([bold]{unique_count}[/bold] unique)\n"
    )
    dup_table = Table(title=f"Duplicates detected ({len(duplicates)})")
    dup_table.add_column("#", style="dim", justify="right")
    dup_table.add_column("Title")
    dup_table.add_column("Artist")
    dup_table.add_column("First at", style="dim", justify="right")

    for idx, track, first_idx in duplicates:
        title = track.get("title", "Unknown")
        artists = ", ".join(a["name"] for a in track.get("artists", []) if a)
        dup_table.add_row(str(idx), title, artists, str(first_idx))

    console.print(dup_table)
    console.print(
        f"\n[yellow]Note: Liked Music will contain {unique_count} songs "
        f"(duplicates are only liked once)[/yellow]\n"
    )
else:
    console.print(f"Found [bold]{len(tracks)}[/bold] songs to import\n")

# Prompt for starting index
while True:
    try:
        start_input = console.input("Start from song number [1]: ").strip()
        if not start_input:
            start_index = 1
        else:
            start_index = int(start_input)
        if 1 <= start_index <= len(tracks):
            break
        console.print(
            f"[red]Please enter a number between 1 and {len(tracks)}[/red]"
        )
    except ValueError:
        console.print("[red]Please enter a valid number[/red]")

if start_index > 1:
    console.print(f"\nStarting from song {start_index}\n")

# Track committed state for verification (0-based index)
start_idx = start_index - 1
committed_index = start_idx

# Like all songs with retry logic and batch verification
i = start_idx
while i < len(tracks):
    track = tracks[i]
    title = track.get("title", "Unknown")
    artists = ", ".join(a["name"] for a in track.get("artists", []) if a)
    video_id = track.get("videoId")

    if not video_id:
        console.print(f"[yellow]Skipping {title} (no video ID)[/yellow]")
        i += 1
        continue

    console.print(
        f"[{i + 1}/{len(tracks)}] Liking: [bold]{title}[/bold] by {artists}"
    )

    # Retry logic for rate_song
    for attempt in range(args.max_retries):
        try:
            yt.rate_song(video_id, LikeStatus.LIKE)
            break
        except Exception as e:
            if attempt == args.max_retries - 1:
                console.print(
                    f"[red]Failed after {args.max_retries} attempts: {e}[/red]"
                )
                raise SystemExit(1)
            console.print(
                f"[yellow]Retry {attempt + 1}/{args.max_retries}...[/yellow]"
            )
            time.sleep(args.delay)

    time.sleep(args.delay)
    i += 1

    # Verify batch when batch_size reached or at end of tracks
    if (i - committed_index) >= args.batch_size or i == len(tracks):
        batch_count = i - committed_index
        console.print(
            f"\n[cyan]Verifying batch of {batch_count} songs...[/cyan]"
        )

        first_failed = verify_likes(yt, tracks, committed_index, batch_count)

        if first_failed is None:
            committed_index = i
            console.print(
                f"[green]Verified! Committed up to song {i}/{len(tracks)}[/green]\n"
            )
        else:
            console.print(
                f"[red]Verification failed at song {first_failed + 1}![/red]"
            )
            console.print(
                f"[yellow]Rolling back songs {first_failed + 1} to {i}...[/yellow]"
            )

            # Unlike from the first failed song onward (with verification)
            rollback_count = i - first_failed
            unlike_batch_with_verification(
                yt, tracks, first_failed, rollback_count, args.delay, console
            )

            # Commit up to the first failed song
            committed_index = first_failed

            console.print(
                f"[yellow]Retrying from song {first_failed + 1}...[/yellow]\n"
            )

            # Reset loop index to retry from first failed song
            i = first_failed

if duplicates:
    console.print(
        f"\n[green]Done! Processed {len(tracks)} songs "
        f"({unique_count} unique added to Liked Music).[/green]"
    )
else:
    console.print(
        f"\n[green]Done! Added {len(tracks)} songs to Liked Music.[/green]"
    )
