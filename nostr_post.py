#!/usr/bin/env python3
"""
nostr_post.py - Read content from stdin and publish it as a Nostr text note.

Requires the NOSTR_NSEC environment variable to be set (bech32 nsec key).

Usage:
  echo "Hello Nostr" | NOSTR_NSEC=nsec1... python nostr_post.py
  python some_bot.py | NOSTR_NSEC=nsec1... python nostr_post.py
"""

import json
import os
import sys

from tornado import gen
from tornado.ioloop import IOLoop
from tornado.websocket import websocket_connect

from pynostr.event import Event
from pynostr.key import PrivateKey

RELAYS = [
    "wss://relay.damus.io",
    "wss://nos.lol",
    "wss://nostr.wine",
]

PUBLISH_WAIT = 2.0   # seconds to wait for OK response from each relay


async def publish_to_relay(url, message):
    """Connect to a single relay, send the event, wait for OK, then close."""
    try:
        ws = await websocket_connect(url, connect_timeout=5)
        await ws.write_message(message)
        # Wait up to PUBLISH_WAIT seconds for an OK/NOTICE response
        try:
            response = await gen.with_timeout(
                IOLoop.current().time() + PUBLISH_WAIT,
                ws.read_message(),
            )
            ws.close()
            if response:
                data = json.loads(response)
                if data[0] == "OK" and data[2] is True:
                    return url, True, ""
                elif data[0] == "OK":
                    return url, False, data[3] if len(data) > 3 else ""
                else:
                    return url, True, f"(got {data[0]})"
            return url, False, "no response"
        except gen.TimeoutError:
            ws.close()
            return url, False, "timeout waiting for OK"
    except Exception as e:
        return url, False, str(e)


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
    event = Event(content=content)
    event.sign(private_key.hex())
    message = event.to_message()

    async def run():
        results = await gen.multi([publish_to_relay(url, message) for url in RELAYS])
        ok = sum(1 for _, success, _ in results if success)
        print(f"Published event {event.id} to {ok}/{len(RELAYS)} relays.", file=sys.stderr)
        for url, success, note in results:
            status = "OK" if success else "FAIL"
            print(f"  {status} {url}{': ' + note if note else ''}", file=sys.stderr)

    IOLoop.current().run_sync(run, timeout=15)


if __name__ == "__main__":
    main()
