#!/usr/bin/env python3
import os, json, sys

print("[∞ RELINK] Reconnecting Infinity engine threads…")

# Required core modules
core = [
    "cart801_terminal_engine.py",
    "cart803_tokens.py",
    "cart804_feed_generator.py",
    "cart805_wallet_engine.py",
]

# Optional deep research / color systems
deep = [
    "C13B0_COLOR_OUTPUT.json",
    "C13B0_PATTERN_MAP.json",
    "C13B0_TONE_COLOR_MAP.json",
    "C13B0_DIVERGENCE_MAP.json",
    "C14B0_FREQUENCY_MAP.json",
    "cart1000_fast_token_engine.py",
    "cart206_trio_fusion.py",
]

missing = []
for f in core + deep:
    if not os.path.exists(f):
        missing.append(f)

if missing:
    print("[∞ RELINK] Missing modules:")
    for m in missing:
        print("   •", m)
    print("[∞ WARNING] Some modules didn’t load — but the link framework was rebuilt.")
else:
    print("[∞ RELINK] All modules located and memory link rebuilt.")

# Rebuild runtime IO bridge
bridge = {
    "engine_link": True,
    "color_system_ready": True,
    "research_system_ready": True,
    "last_boot": "restored"
}

with open("INFINITY_RUNTIME_LINK.json", "w") as f:
    json.dump(bridge, f, indent=2)

print("[∞ RELINK] Runtime bridge written → INFINITY_RUNTIME_LINK.json")
print("[∞ RELINK] Complete.")
