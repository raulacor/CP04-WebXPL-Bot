# Black Hands the Bot

A Discord bot that brings offensive reconnaissance tooling into your server. It exposes common recon tools as slash commands, returning results as clean file attachments or embedded cards.

Built for the FIAP Web Exploitation coursework. Library: [discord.py](https://discordpy.readthedocs.io/en/stable/index.html).

> ⚠️ **Use responsibly.** Only scan, enumerate, or probe targets you own or have explicit written permission to test. Unauthorized scanning may be illegal.

---

## Commands

| Command         | Argument   | Description                                                                                               |
| --------------- | ---------- | --------------------------------------------------------------------------------------------------------- |
| `/nmap`         | `<host>`   | Runs a service/version scan (`nmap -sV`) and returns the report as a file.                                |
| `/gau`          | `<domain>` | Collects known endpoints/URLs passively via [gau](https://github.com/lc/gau); returns a file.             |
| `/crt`          | `<domain>` | Queries [crt.sh](https://crt.sh) certificate logs to enumerate subdomains (deduplicated); returns a file. |
| `/ipinfo`       | `<ip>`     | Looks up geolocation and network info for an IP via [ipinfo.io](https://ipinfo.io).                       |
| `/dependencies` | —          | Installs the required CLI tools (`nmap`, `golang`, `gau`) on Debian/Ubuntu.                               |
| `/help`         | —          | Shows a card listing all available commands.                                                              |

### Examples

```
/nmap scanme.nmap.org
/gau example.com
/crt fiap.com.br
/ipinfo 8.8.8.8
```

---

## Requirements

**Runtime**

- Python 3.10+

**Python libraries** (see `requirements.txt`)

- `discord.py` — Discord bot framework
- `python-dotenv` — loads the bot token from `.env`
- `requests` — HTTP calls for `/ipinfo` and `/crt`

**External CLI tools** (must be on your `PATH`)

- `nmap` — used by `/nmap`
- `gau` — used by `/gau` (Go binary: `go install github.com/lc/gau/v2/cmd/gau@latest`)
- `go` — required to install `gau`

> The `/dependencies` command installs `nmap`, `golang` and `gau` automatically on Debian/Ubuntu (requires passwordless sudo).

**Discord setup**

- A bot token stored in `.env` as `DISCORD_TOKEN`
- `MESSAGE CONTENT` intent enabled in the Discord Developer Portal

---

## How to run locally

1. **Clone the repo**

   ```bash
   git clone https://github.com/<your-user>/CP04-Web-XPL-Bot.git
   cd CP04-Web-XPL-Bot
   ```

2. **Install Python dependencies**

   ```bash
   pip install -r requirements.txt
   ```

3. **Install the external CLI tools** (Debian/Ubuntu)

   ```bash
   sudo apt update && sudo apt install -y nmap golang
   go install github.com/lc/gau/v2/cmd/gau@latest
   ```

   Or run the `/dependencies` command once the bot is online.

4. **Create your `.env` file** (see `.env_template`)

   ```
   DISCORD_TOKEN=your_bot_token_here
   ```

   Get the token from the [Discord Developer Portal](https://discord.com/developers/applications) → your app → **Bot** → **Reset Token**.

5. **Enable intents** in the Developer Portal → **Bot** → **Privileged Gateway Intents** → turn on **MESSAGE CONTENT**.

6. **Run the bot**
   ```bash
   python src/main.py
   ```
   On startup the bot syncs its slash commands; they should appear in your server's `/` picker within a moment.

---

## Project structure

```
CP04-Web-XPL-Bot/
├── src/
│   └── main.py          # Bot entry point and all command definitions
├── requirements.txt     # Python dependencies
├── .env_template        # Template for your DISCORD_TOKEN
├── .env                 # Your actual token (git-ignored)
└── README.md
```

**How the bot is organized**

- A single `commands.Bot` instance holds every command.
- Each command is registered as a slash command with `@bot.tree.command(...)`; `on_ready` calls `bot.tree.sync()` to publish them to Discord.
- Long-running tool commands (`/nmap`, `/gau`) `defer` first (to beat Discord's 3-second response limit), run the tool via `subprocess`, and return the output as an in-memory file attachment — nothing is written to disk.
- API commands (`/ipinfo`, `/crt`) use `requests` and check the HTTP status before parsing JSON.
- Every command has basic error handling: a `try/except` for tools/services that can't run or be reached, and a status/return-code check for runs that fail cleanly.
