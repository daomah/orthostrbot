#!/usr/bin/env python3
"""
nostr_post.py - Read content from stdin and publish it as a Nostr text note.

Requires the NOSTR_NSEC environment variable to be set (bech32 nsec key).

Usage:
  echo "Hello Nostr" | NOSTR_NSEC=nsec1... python nostr_post.py
  python some_bot.py | NOSTR_NSEC=nsec1... python nostr_post.py
"""

import os
import sys
import time

from pynostr.event import Event
from pynostr.key import PrivateKey
from pynostr.relay_manager import RelayManager

RELAYS = [
    "wss://relay.damus.io",
    "wss://nos.lol",
    "wss://relay.nostr.band",
    "wss://nostr.wine",
]

CONNECT_WAIT = 1.5   # seconds to wait for relay connections to open
PUBLISH_WAIT = 1.5   # seconds to wait for event propagation


def main():
    nsec = os.environ.get("NOSTR_NSEC")
    if not nsec:
        print("Error: NOSTR_NSEC environment variable not set.", file=sys.stderr)
        sys.exit(1)

    content = sys.stdin.read().strip()
    if not content:
        print("Error: no content on stdin.", file=sys.stderr)
        sys.exit(1)

    private_key = PrivateKey.from_nsec(nsec)

    relay_manager = RelayManager(error_threshold=2)
    for url in RELAYS:
        relay_manager.add_relay(url)

    relay_manager.open_connections()
    time.sleep(CONNECT_WAIT)

    event = Event(content=content)
    private_key.sign_event(event)
    relay_manager.publish_event(event)
    print(f"Published event {event.id} to {len(RELAYS)} relays.", file=sys.stderr)

    time.sleep(PUBLISH_WAIT)
    relay_manager.close_connections()


if __name__ == "__main__":
    main()
