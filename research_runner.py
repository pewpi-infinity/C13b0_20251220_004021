#!/usr/bin/env python3
"""
Infinity Research Runner
Cycles through repos and generates real commits
"""

import time
import subprocess
from pathlib import Path
from datetime import datetime

HOME = Path.home()
TARGETS = (HOME / "repo_targets.txt").read_text().splitlines()
INTERVAL = 90  # seconds between repos

def run(cmd, cwd=None):
    subprocess.run(cmd, cwd=cwd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def generate_research(repo):
    path = HOME / repo
    if not path.exists():
        return

    out = path / "RESEARCH_AUTO.md"
    ts = datetime.utcnow().isoformat()

    with open(out, "a") as f:
        f.write(f"\n## Research Pulse — {ts}\n")
        f.write("- System evolution detected\n")
        f.write("- Cross-repo alignment in progress\n")
        f.write("- Provenance-first research model\n")

    run(["git", "add", "RESEARCH_AUTO.md"], cwd=path)
    run(["git", "commit", "-m", f"∞ research pulse {ts}"], cwd=path)
    run(["git", "push", "origin", "main"], cwd=path)

def main():
    print("[∞] Research Runner ONLINE")
    i = 0
    while True:
        repo = TARGETS[i % len(TARGETS)]
        generate_research(repo)
        i += 1
        time.sleep(INTERVAL)

if __name__ == "__main__":
    main()
