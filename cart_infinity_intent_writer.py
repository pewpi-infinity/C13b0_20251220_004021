#!/usr/bin/env python3
import sys, random
from pathlib import Path
from datetime import datetime, timezone

TYPES = [
  ("Research",      "🟦", ["hydrogen pressure mapping", "quantum orbital storage", "entropy capture pathways", "field regime analyzer"]),
  ("Engineering",   "🟩", ["firmware wiring pass", "repo-to-repo linking", "index stabilization", "token writer hardening"]),
  ("Assimilation",  "🟪", ["vector assimilation step", "symbolic convergence", "octave mapping layer", "multi-repo choreography"]),
  ("Mining",        "🟨", ["hash stream semantics", "difficulty dial logic", "block timing rhythm", "proof-of-work narrative"]),
  ("Decisions",     "🟧", ["routing options review", "priority queue update", "risk filter", "deployment path choice"]),
  ("Investigative", "🩷", ["source validation", "pump-detection notes", "integrity scoring", "trust graph update"]),
]

def now():
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

def pick():
    kind, emoji, topics = random.choice(TYPES)
    topic = random.choice(topics)
    return kind, emoji, topic

def append_line(p: Path, line: str):
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(line)

def main():
    if len(sys.argv) < 2:
        print("usage: cart_infinity_intent_writer.py /path/to/repo")
        return 2

    repo = Path(sys.argv[1])
    kind, emoji, topic = pick()
    ts = now()

    # 1) stream file = visible growth
    stream = repo / "RESEARCH_STREAM.md"
    append_line(stream, f"{emoji} **[{kind}]** {ts} — {topic}\n")

    # 2) index hook = helps GH Pages / browsing later
    idx = repo / "site" / "index.md"
    append_line(idx, f"- {emoji} [{kind}] {ts} — {topic}\n")

    # 3) ledger-like pulse = your “flying numbers”
    led = repo / "LEDGER.md"
    append_line(led, f"{ts} | {emoji} {kind} | {topic}\n")

    return 0

if __name__ == "__main__":
    raise SystemExit(main())
