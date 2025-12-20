#!/usr/bin/env python3
import time, random, subprocess
from pathlib import Path
from datetime import datetime, timezone

HOME = Path.home()
TYPES = [
    ("Research", "🟦", "hydrogen field dynamics"),
    ("Engineering", "🟩", "system coupling logic"),
    ("Assimilation", "🟪", "symbolic convergence"),
    ("Mining", "🟨", "proof-of-work semantics"),
]

def sh(cmd, cwd=None):
    try:
        r = subprocess.run(cmd, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, text=True)
        return r.stdout.strip()
    except:
        return ""

def is_repo(p):
    return sh(["git","-C",str(p),"rev-parse","--is-inside-work-tree"]) and sh(["git","-C",str(p),"rev-parse","HEAD"])

while True:
    for repo in HOME.iterdir():
        if not repo.is_dir(): continue
        if not (repo.name.startswith("infinity") or repo.name == "mongoose.os"): continue
        if not is_repo(repo): continue

        kind, color, topic = random.choice(TYPES)
        ts = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")

        f = repo / "RESEARCH_STREAM.md"
        line = f"{color} [{kind}] {ts} — {topic}\n"

        f.write_text(f.read_text() + line if f.exists() else line)

        sh(["git","-C",str(repo),"add","RESEARCH_STREAM.md"])
        sh(["git","-C",str(repo),"commit","-m",f'{kind}: {topic}'])
        sh(["git","-C",str(repo),"push","origin","main"])

        time.sleep(2)  # rhythm

    time.sleep(30)
