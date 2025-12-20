#!/usr/bin/env python3
import json, random, itertools

print("[∞ Topic-250] Generating 250 search terms + 250 equations…")

terms = [
    "hydrogen","frequency","ionization","singularity","resonance","portal",
    "acoustic field","quantum gate","electron doorway","hydrogen portal",
    "cosmic drift","silver lattice","gold lattice","neutrino fold",
    "sound pressure","talent signal","Phil Collins","percussion phase",
    "vocal timbre","harmonics","thermal shift","gravity shear","ion field",
    "magnetic aperture","scalar bloom","tachyon trace","energy lens",
    "particle anchor","vacuum shape","chronon ripple","gamma bridge",
    "infra band","ultra band","voltage symmetry","oxide channel"
]

# Expand to 250 unique concept nodes
while len(terms) < 250:
    base = random.choice(terms)
    mod = random.choice(["phase","gate","vector","node","layer","cycle","shift"])
    terms.append(f"{base} {mod}")

equations = []
ops = ["+", "-", "×", "÷"]

while len(equations) < 250:
    a = random.choice(terms)
    b = random.choice(terms)
    op = random.choice(ops)
    equations.append(f"{a} {op} {b}")

matrix = {
    "total_terms": len(terms),
    "total_equations": len(equations),
    "terms": terms,
    "equations": equations,
    "cross_pairs": []
}

# Build cross-pairs (big node expansion)
pairs = list(itertools.combinations(terms[:50], 2))
matrix["cross_pairs"] = [f"{a} ∧ {b}" for a,b in random.sample(pairs, 200)]

with open("CART250_TOPIC_MATRIX.json", "w") as f:
    json.dump(matrix, f, indent=2)

print("[∞ Topic-250] Saved → CART250_TOPIC_MATRIX.json")
