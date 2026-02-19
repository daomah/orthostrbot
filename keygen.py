#!/usr/bin/env python3
"""
keygen.py - Generate a new Nostr keypair and save the nsec to
~/.config/nostr-bot/keys.env with 600 permissions.

Run this once on the posting machine to set up credentials.
"""

from pathlib import Path

from pynostr.key import PrivateKey


def main():
    key = PrivateKey()
    nsec = key.bech32()
    npub = key.public_key.bech32()

    print(f"npub (public key):  {npub}")
    print(f"nsec (private key): {nsec}")

    config_dir = Path.home() / ".config" / "nostr-bot"
    config_dir.mkdir(parents=True, exist_ok=True)

    keys_file = config_dir / "keys.env"
    keys_file.write_text(f"NOSTR_NSEC={nsec}\n")
    keys_file.chmod(0o600)

    print(f"\nSaved nsec to {keys_file} (mode 600)")
    print("\nIMPORTANT: Back up your nsec securely. It cannot be recovered if lost.")
    print("Share only your npub (public key) — never your nsec.")


if __name__ == "__main__":
    main()
