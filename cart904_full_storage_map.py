#!/usr/bin/env python3
import os

roots = [
    "/data/data/com.termux/files/home",
    "/storage/emulated/0",
    "/sdcard",
]

print("[cart904] Full-device scan for files > 5MB...")
found = []

for root in roots:
    if not os.path.isdir(root):
        continue
    print(f"[cart904] Scanning {root} ...")
    for dirpath, dirnames, filenames in os.walk(root):
        for name in filenames:
            try:
                full = os.path.join(dirpath, name)
                size = os.path.getsize(full)
                if size >= 5 * 1024 * 1024:   # 5MB+
                    found.append((size, full))
            except:
                pass

if not found:
    print("[cart904] ❌ No large files found.")
else:
    found.sort(reverse=True)  # biggest first
    print(f"[cart904] ✅ Found {len(found)} large files:")
    for size, path in found:
        print(f"{size}\t{path}")
