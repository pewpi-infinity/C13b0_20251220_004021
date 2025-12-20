#!/usr/bin/env python3
import os
import sys
import zipfile

def log(msg):
    print(f"[cart902] {msg}", flush=True)

# If you pass a directory as arg, use that. Otherwise search common Infinity dirs.
if len(sys.argv) > 1:
    roots = [os.path.abspath(os.path.expanduser(sys.argv[1]))]
else:
    roots = [
        os.path.expanduser("~/z/z"),
        os.path.expanduser("~/z"),
        os.path.expanduser("~/o"),
        os.path.expanduser("~/v"),
        os.path.expanduser("~/y"),
    ]

log("Searching for zip_coin_*.zip files...")
found_files = []

for root in roots:
    if not os.path.isdir(root):
        continue
    log(f"  Scanning {root} ...")
    for dirpath, dirnames, filenames in os.walk(root):
        for name in filenames:
            if name.startswith("zip_coin_") and name.endswith(".zip"):
                found_files.append(os.path.join(dirpath, name))

if not found_files:
    log("❌ No zip_coin_*.zip files found under any of the search roots.")
    sys.exit(1)

# Sort files for stable packet ordering
found_files = sorted(found_files)
log(f"✅ Found {len(found_files)} zip_coin_*.zip files total.")

# Decide packet output directory.
# Use the parent of the directory where the first file lives.
first_dir = os.path.dirname(found_files[0])
base_dir = os.path.dirname(first_dir)
packet_dir = os.path.join(base_dir, "packets_cart889")
os.makedirs(packet_dir, exist_ok=True)

log(f"Packets will be written to: {packet_dir}")

packet_size = 1000
packet_index = 0
current_zip = None
files_in_current = 0

def open_new_packet():
    global packet_index, current_zip, files_in_current
    if current_zip is not None:
        current_zip.close()
    packet_index += 1
    files_in_current = 0
    packet_name = f"packet_{packet_index:03d}.zip"
    packet_path = os.path.join(packet_dir, packet_name)
    log(f"→ Starting {packet_name}")
    current_zip_local = zipfile.ZipFile(packet_path, "w", compression=zipfile.ZIP_DEFLATED)
    return current_zip_local

current_zip = open_new_packet()

for i, fpath in enumerate(found_files, start=1):
    arcname = os.path.basename(fpath)
    try:
        current_zip.write(fpath, arcname=arcname)
    except Exception as e:
        log(f"⚠️ Error adding {fpath}: {e}")
        continue

    files_in_current += 1
    if files_in_current >= packet_size:
        current_zip.close()
        current_zip = open_new_packet()

    if i % 100 == 0:
        log(f"  Processed {i} files...")

# Close last packet
if current_zip is not None:
    current_zip.close()

log(f"✅ Done. Created {packet_index} packet zip(s) in {packet_dir}.")
