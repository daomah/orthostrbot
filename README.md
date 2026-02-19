# orthostrbot

Publishes daily Orthodox Christian content to [Nostr](https://nostr.com) — the saint of the day and the scripture readings — on a scheduled basis using systemd timers.

## What it does

Two posts go out each day:

1. **6:00 AM** — the top saint of the day (name, icon, troparion, kontakion), sourced via [daily_saint_bot](https://github.com/daomah/daily_saint_bot)
2. **9:00 AM** — the full scripture readings for the day (Epistle, Gospel, and all other types), sourced via [daily_readings_bot](https://github.com/daomah/daily_readings_bot)

Each post is signed with a Nostr private key and broadcast to multiple public relays.

## Usage

### Post manually

```bash
# Saint post
python3 ~/git/personal/daily_saint_bot/bot.py | NOSTR_NSEC=nsec1... python3 nostr_post.py

# Readings post
python3 ~/git/personal/daily_readings_bot/bot.py | NOSTR_NSEC=nsec1... python3 nostr_post.py
```

Or load the key from the saved env file:

```bash
python3 ~/git/personal/daily_saint_bot/bot.py | \
  env $(cat ~/.config/nostr-bot/keys.env) python3 nostr_post.py
```

### Check scheduled posts

```bash
systemctl --user list-timers
journalctl --user -u daily-saint.service
journalctl --user -u daily-readings.service
```

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Clone the content bots

```bash
git clone https://github.com/daomah/daily_saint_bot ~/git/personal/daily_saint_bot
git clone https://github.com/daomah/daily_readings_bot ~/git/personal/daily_readings_bot
pip install -r ~/git/personal/daily_saint_bot/requirements.txt
pip install -r ~/git/personal/daily_readings_bot/requirements.txt
```

### 3. Generate a Nostr keypair

```bash
python3 keygen.py
```

This creates `~/.config/nostr-bot/keys.env` containing your `NOSTR_NSEC`. Back up the nsec securely — it cannot be recovered if lost. Share only your npub (public key).

### 4. Install the systemd user units

```bash
mkdir -p ~/.config/systemd/user
cp systemd/*.service systemd/*.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now daily-saint.timer daily-readings.timer
```

### 5. Allow posts to run without an active login session

```bash
loginctl enable-linger $USER
```

## How it works

### nostr_post.py

Reads content from stdin, signs it as a Nostr kind-1 text note using the private key in `NOSTR_NSEC`, and broadcasts it to four public relays:

- `wss://relay.damus.io`
- `wss://nos.lol`
- `wss://relay.nostr.band`
- `wss://nostr.wine`

### systemd units

Two `.service` / `.timer` pairs run as user-level systemd units. Each service pipes a content bot's stdout directly into `nostr_post.py`. `Persistent=true` on the timers ensures a missed post fires on next boot.

### keygen.py

One-time utility that generates a fresh secp256k1 keypair, prints the bech32-encoded npub and nsec, and saves the nsec to `~/.config/nostr-bot/keys.env` with mode 600.

## Resources

| Resource | URL |
|---|---|
| Nostr protocol | https://nostr.com |
| pynostr library | https://github.com/holgern/pynostr |
| daily_saint_bot | https://github.com/daomah/daily_saint_bot |
| daily_readings_bot | https://github.com/daomah/daily_readings_bot |

## License

The **code** in this repository is released under the [MIT License](LICENSE).
