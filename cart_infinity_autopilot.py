#!/usr/bin/env python3
"""
Infinity Autopilot Core
Watches Infinity system and triggers automation
"""

import time
import subprocess
from pathlib import Path

WATCH_DIRS = [
    Path.home() / "infinity_mongoose_bitcoin_research_miner",
    Path.home() / "infinity_blank_grade_research_miner",
    Path.home() / "mongoose.os",
]

INTERVAL = 10
STATE_FILE = Path.home() / ".infinity_autopilot_state"

def snapshot():
    state = {}
    for d in WATCH_DIRS:
        if d.exists():
            state[str(d)] = sum(
                p.stat().st_mtime
                for p in d.rglob("*")
                if p.is_file()
            )
    return state

def load_state():
    if STATE_FILE.exists():
        return eval(STATE_FILE.read_text())
    return {}

def save_state(s):
    STATE_FILE.write_text(repr(s))

def trigger():
    print("[∞] Change detected → autopilot running")
    subprocess.call([str(Path.home() / "cart_auto_research_writer.sh")])
    subprocess.call([str(Path.home() / "cart_auto_tokenize.sh")])
    subprocess.call([str(Path.home() / "cart_push_all_repos.sh")])

def main():
    print("[∞] Infinity Autopilot ONLINE")
    last = load_state()

    while True:
        now = snapshot()
        if now != last:
            trigger()
            save_state(now)
            last = now
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
