# orthostrbot

Publishes daily Orthodox Christian content to [Nostr](https://nostr.com) — the saint of the day and the scripture readings — on a scheduled basis using systemd timers.

## What it does

Three posts go out each day:

1. **6:00 AM** — the top saint of the day (name, icon, troparion, kontakion), sourced via [daily_saint_bot](https://github.com/daomah/daily_saint_bot)
2. **9:00 AM** — the full scripture readings for the day (Epistle, Gospel, and all other types), sourced via [daily_readings_bot](https://github.com/daomah/daily_readings_bot)
3. **4:00 PM** — a randomly selected lesser-commemorated saint of the day, sourced via [daily_saint_bot](https://github.com/daomah/daily_saint_bot) `--random`

Each post is signed with a Nostr private key and broadcast to multiple public relays.

## Usage

### Post manually

```bash
# Top saint post
~/git/personal/daily_saint_bot/.venv/bin/python ~/git/personal/daily_saint_bot/bot.py | \
  NOSTR_NSEC=nsec1... .venv/bin/python nostr_post.py

# Random saint post
~/git/personal/daily_saint_bot/.venv/bin/python ~/git/personal/daily_saint_bot/bot.py --random | \
  NOSTR_NSEC=nsec1... .venv/bin/python nostr_post.py

# Readings post
~/git/personal/daily_readings_bot/.venv/bin/python ~/git/personal/daily_readings_bot/bot.py | \
  NOSTR_NSEC=nsec1... .venv/bin/python nostr_post.py
```

Or load the key from the saved env file:

```bash
~/git/personal/daily_saint_bot/.venv/bin/python ~/git/personal/daily_saint_bot/bot.py --random | \
  env $(cat ~/.config/nostr-bot/keys.env) .venv/bin/python nostr_post.py
```

### Check scheduled posts

```bash
systemctl --user list-timers
journalctl --user -u daily-saint.service
journalctl --user -u daily-saint-random.service
journalctl --user -u daily-readings.service
```

## Setup

### 1. Install dependencies

```bash
python3 -m venv .venv
.venv/bin/pip install -r requirements.txt
```

### 2. Clone the content bots

```bash
git clone https://github.com/daomah/daily_saint_bot ~/git/personal/daily_saint_bot
cd ~/git/personal/daily_saint_bot && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt

git clone https://github.com/daomah/daily_readings_bot ~/git/personal/daily_readings_bot
cd ~/git/personal/daily_readings_bot && python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
```

### 3. Generate a Nostr keypair

```bash
python3 keygen.py
```

This creates `~/.config/nostr-bot/keys.env` containing your `NOSTR_NSEC`. Back up the nsec securely — it cannot be recovered if lost. Share only your npub (public key).

### 4. Install the systemd user units

The service files assume the repos are cloned under `~/git/personal/`. If you used a different location, edit the `ExecStart` lines in the `.service` files before copying.

```bash
mkdir -p ~/.config/systemd/user
cp systemd/*.service systemd/*.timer ~/.config/systemd/user/
systemctl --user daemon-reload
systemctl --user enable --now daily-saint.timer daily-saint-random.timer daily-readings.timer
```

### 5. Allow posts to run without an active login session

```bash
loginctl enable-linger $USER
```

## How it works

### nostr_post.py

Reads content from stdin, signs it as a Nostr kind-1 text note using the private key in `NOSTR_NSEC`, and broadcasts it to public relays:

- `wss://relay.damus.io`
- `wss://nos.lol`
- `wss://nostr.wine` (requires a free account at nostr.wine to write)

### systemd units

Three `.service` / `.timer` pairs run as user-level systemd units. Each service pipes a content bot's stdout directly into `nostr_post.py`. `Persistent=true` on the timers ensures a missed post fires on next boot.

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
