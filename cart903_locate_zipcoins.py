#!/usr/bin/env python3
import os

roots = [
    "/data/data/com.termux/files/home",
    "/storage/emulated/0",
    "/sdcard",
]

print("[cart903] Deep scanning for zip_coin_*.zip ...")
matches = []

for root in roots:
    if not os.path.isdir(root):
        continue
    print(f"[cart903] Scanning {root} ...")
    for dirpath, dirnames, filenames in os.walk(root):
        for name in filenames:
            if name.startswith("zip_coin_") and name.endswith(".zip"):
                full = os.path.join(dirpath, name)
                matches.append(full)

if not matches:
    print("[cart903] ❌ No zip_coin_*.zip files found anywhere in accessible storage.")
else:
    print(f"[cart903] ✅ Found {len(matches)} files:")
    for m in matches:
        print(m)
