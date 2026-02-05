import json
import os

from rich.console import Console

console = Console()

if os.path.exists("browser.json"):
    console.print("[yellow]browser.json already exists.[/yellow]")
    overwrite = console.input("Overwrite? (y/N): ").strip().lower()
    if overwrite not in ("y", "yes"):
        raise SystemExit(0)

console.print("[bold]YouTube Music Browser Authentication Setup[/bold]\n")
console.print("1. Open https://music.youtube.com and log in")
console.print("2. Open DevTools (F12) > Network tab")
console.print(
    '3. Click "Home" or "Explore" in the left sidebar'
)
console.print(
    '4. Find the "/browse" POST request and click it'
)
console.print(
    "5. Copy the Authorization and Cookie headers\n"
)

authorization = console.input("Authorization: ").strip()
cookie = console.input("Cookie: ").strip()

if not authorization:
    raise SystemExit("[red]Authorization is required[/red]")
if not cookie:
    raise SystemExit("[red]Cookie is required[/red]")

browser_json = {
    "Accept": "*/*",
    "Authorization": authorization,
    "Content-Type": "application/json",
    "X-Goog-AuthUser": "0",
    "x-origin": "https://music.youtube.com",
    "Cookie": cookie,
}

with open("browser.json", "w") as f:
    json.dump(browser_json, f, indent=4)

console.print("\n[green]Saved browser.json[/green]")
console.print(
    "[dim]Credentials are valid for ~2 years" " unless you log out.[/dim]"
)
