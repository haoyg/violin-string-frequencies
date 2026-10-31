#!/usr/bin/env python3
"""Generate violin string frequency tables.

Every number in data/ and in the README tables comes from this script.
Equal temperament: f = A4 * 2 ** (n / 12), where n is semitones from A4.
Pure fifths (how violinists actually tune by ear): each string is a 3:2
fifth from its neighbour, anchored on the A string.

Usage:
    python3 scripts/generate.py           # write data/ and README tables
    python3 scripts/generate.py --check   # exit 1 if anything is out of date
"""

import csv
import io
import json
import math
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
README = ROOT / "README.md"

REFERENCE_PITCHES = [415, 440, 441, 442]
DECIMALS = 2

NOTE_OFFSETS = {"C": -9, "C#": -8, "D": -7, "D#": -6, "E": -5, "F": -4,
                "F#": -3, "G": -2, "G#": -1, "A": 0, "A#": 1, "B": 2}

STANDARD = ["G3", "D4", "A4", "E5"]

# Strings listed low to high (IV, III, II, I).
CROSS_TUNINGS = {
    "AEAE": ["A3", "E4", "A4", "E5"],
    "GDGD": ["G3", "D4", "G4", "D5"],
    "ADAD": ["A3", "D4", "A4", "D5"],
    "ADAE": ["A3", "D4", "A4", "E5"],
    "GDAD": ["G3", "D4", "A4", "D5"],
}

STRING_NAMES = ["IV", "III", "II", "I"]


def semitones_from_a4(note):
    m = re.fullmatch(r"([A-G]#?)(-?\d)", note)
    if not m:
        raise ValueError(f"bad note name: {note}")
    name, octave = m.group(1), int(m.group(2))
    return NOTE_OFFSETS[name] + 12 * (octave - 4)


def et_freq(note, a4):
    return a4 * 2 ** (semitones_from_a4(note) / 12)


def cents(f, ref):
    return 1200 * math.log2(f / ref)


def pure_fifths(a4):
    """G-D-A-E tuned in 3:2 fifths from A4."""
    d = a4 * 2 / 3
    return {"G3": d * 2 / 3, "D4": d, "A4": a4, "E5": a4 * 3 / 2}


def r(x):
    return round(x, DECIMALS)


def build():
    standard = {}
    for a4 in REFERENCE_PITCHES:
        pure = pure_fifths(a4)
        standard[str(a4)] = [
            {
                "string": STRING_NAMES[i],
                "note": note,
                "semitones_from_a4": semitones_from_a4(note),
                "equal_hz": r(et_freq(note, a4)),
                "pure_fifths_hz": r(pure[note]),
                "pure_vs_equal_cents": r(cents(pure[note], et_freq(note, a4))),
                "cents_vs_a440": r(cents(a4, 440)),
            }
            for i, note in enumerate(STANDARD)
        ]

    cross = {}
    for name, notes in CROSS_TUNINGS.items():
        cross[name] = {
            str(a4): [
                {
                    "string": STRING_NAMES[i],
                    "note": note,
                    "equal_hz": r(et_freq(note, a4)),
                    "change_from_gdae_semitones":
                        semitones_from_a4(note) - semitones_from_a4(STANDARD[i]),
                }
                for i, note in enumerate(notes)
            ]
            for a4 in REFERENCE_PITCHES
        }

    return {
        "meta": {
            "generator": "scripts/generate.py",
            "formula": "f = A4 * 2^(n/12); pure fifths = A4 * (2/3)^k",
            "decimals": DECIMALS,
            "reference_pitches_hz": REFERENCE_PITCHES,
            "license": "MIT",
            "source": "https://violin-tuner.com/",
        },
        "standard_gdae": standard,
        "cross_tunings": cross,
    }


def to_csv(rows, fields):
    buf = io.StringIO()
    w = csv.DictWriter(buf, fieldnames=fields, lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return buf.getvalue()


def render_files(data):
    files = {}
    files[DATA / "violin-frequencies.json"] = json.dumps(data, indent=2) + "\n"

    std_rows = [{"a4_hz": a4, **row}
                for a4, rows in data["standard_gdae"].items() for row in rows]
    files[DATA / "standard-gdae.csv"] = to_csv(
        std_rows, ["a4_hz", "string", "note", "semitones_from_a4", "equal_hz",
                   "pure_fifths_hz", "pure_vs_equal_cents", "cents_vs_a440"])

    cross_rows = [{"tuning": t, "a4_hz": a4, **row}
                  for t, by_pitch in data["cross_tunings"].items()
                  for a4, rows in by_pitch.items() for row in rows]
    files[DATA / "cross-tunings.csv"] = to_csv(
        cross_rows, ["tuning", "a4_hz", "string", "note", "equal_hz",
                     "change_from_gdae_semitones"])
    return files


def fmt(x):
    return f"{x:.{DECIMALS}f}"


def md_table(header, rows):
    lines = ["| " + " | ".join(header) + " |",
             "|" + "|".join("---:" if i else "---" for i in range(len(header))) + "|"]
    lines += ["| " + " | ".join(row) + " |" for row in rows]
    return "\n".join(lines)


def readme_tables(data):
    std = data["standard_gdae"]
    out = {}

    out["standard"] = md_table(
        ["String", "Note"] + [f"A={a} Hz" for a in REFERENCE_PITCHES],
        [[STRING_NAMES[i], note] + [fmt(std[str(a)][i]["equal_hz"]) for a in REFERENCE_PITCHES]
         for i, note in enumerate(STANDARD)])

    out["cents"] = md_table(
        ["Reference", "Ratio to 440", "Cents vs A=440"],
        [[f"A={a} Hz", f"{a}/440 = {a / 440:.6f}", f"{cents(a, 440):+.2f}"]
         for a in REFERENCE_PITCHES])

    out["pure"] = md_table(
        ["Note", "Equal (A=440)", "Pure fifths (A=440)", "Pure − equal (cents)",
         "Equal (A=442)", "Pure fifths (A=442)"],
        [[note,
          fmt(std["440"][i]["equal_hz"]), fmt(std["440"][i]["pure_fifths_hz"]),
          f"{std['440'][i]['pure_vs_equal_cents']:+.2f}",
          fmt(std["442"][i]["equal_hz"]), fmt(std["442"][i]["pure_fifths_hz"])]
         for i, note in enumerate(STANDARD)])

    rows = []
    for name, by_pitch in data["cross_tunings"].items():
        for a in ("440", "442"):
            cells = [f"{s['note']} {fmt(s['equal_hz'])}" for s in by_pitch[a]]
            rows.append([name, a] + cells)
    out["cross"] = md_table(["Tuning", "A (Hz)", "IV", "III", "II", "I"], rows)
    return out


def update_readme(text, tables):
    for key, table in tables.items():
        pattern = re.compile(
            rf"(<!-- BEGIN {key} -->\n)(?:.*?\n)?(<!-- END {key} -->)", re.S)
        if not pattern.search(text):
            raise SystemExit(f"README is missing the <!-- BEGIN {key} --> marker")
        text = pattern.sub(lambda m: m.group(1) + table + "\n" + m.group(2), text)
    return text


def main():
    check = "--check" in sys.argv[1:]
    data = build()
    outputs = render_files(data)
    outputs[README] = update_readme(README.read_text(), readme_tables(data))

    stale = [p for p, content in outputs.items()
             if not p.exists() or p.read_text() != content]
    if check:
        for p in stale:
            print(f"out of date: {p.relative_to(ROOT)}")
        sys.exit(1 if stale else 0)

    DATA.mkdir(exist_ok=True)
    for p in stale:
        p.write_text(outputs[p])
        print(f"wrote {p.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
