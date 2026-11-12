"""Compare two runs of the bench case by case.

Reads the results.csv of each run and writes a Markdown report: how many cases changed, the counts per mode
and per size, every changed case with both scores, and whether any case crossed the pass mark.

Usage: uv run python compare.py results results-tesseract-5.5.4 [--out results-tesseract-5.5.4/comparison.md]
"""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from bench import MODES, SURVIVES, smallest_surviving

Case = tuple[str, int, str]


def load(run: Path) -> dict[Case, dict[str, str]]:
    with (run / "results.csv").open(newline="") as fh:
        return {(r["face"], int(r["size_pt"]), r["mode"]): r for r in csv.DictReader(fh)}


def changed(a: dict[Case, dict[str, str]], b: dict[Case, dict[str, str]]) -> list[tuple[Case, int, int]]:
    """Cases whose edit distance differs, in the order of the first run. Both runs must hold the same cases."""
    if a.keys() != b.keys():
        raise SystemExit("the two runs do not hold the same cases")
    if any(a[k]["truth_chars"] != b[k]["truth_chars"] for k in a):
        raise SystemExit("the two runs do not score against the same passage")
    return [(k, int(a[k]["edit_distance"]), int(b[k]["edit_distance"])) for k in a if a[k]["edit_distance"] != b[k]["edit_distance"]]


def passes(row: dict[str, str]) -> bool:
    return float(row["char_accuracy"]) >= SURVIVES


def summary(a: dict[Case, dict[str, str]], b: dict[Case, dict[str, str]]) -> dict[str, object]:
    diff = changed(a, b)
    faces = list(dict.fromkeys(k[0] for k in a))
    rows_a, rows_b = list(a.values()), list(b.values())
    return {
        "cases": len(a),
        "changed": len(diff),
        "fewer_errors": sum(1 for _, x, y in diff if y < x),
        "more_errors": sum(1 for _, x, y in diff if y > x),
        "total_errors": [sum(int(r["edit_distance"]) for r in rows_a), sum(int(r["edit_distance"]) for r in rows_b)],
        "changed_by_mode": {m.name: sum(1 for k, _, _ in diff if k[2] == m.name) for m in MODES},
        "largest_change_points": max((abs(float(b[k]["char_accuracy"]) - float(a[k]["char_accuracy"])) * 100 for k, _, _ in diff), default=0.0),
        "crossed_pass_mark": [list(k) for k, _, _ in diff if passes(a[k]) != passes(b[k])],
        "smallest_passing_size_changed": [
            [face, m.name] for face in faces for m in MODES
            if smallest_surviving(rows_a, face, m.name) != smallest_surviving(rows_b, face, m.name)  # type: ignore[arg-type]
        ],
    }


def environment(run: Path) -> dict[str, object]:
    return dict(json.loads((run / "environment.json").read_text()))


def tool(run: Path) -> str:
    return str(environment(run)["tesseract"])


def same_passage(run_a: Path, run_b: Path) -> None:
    """Two runs can be compared only when both scored against the same passage file."""
    if environment(run_a)["passage_sha256"] != environment(run_b)["passage_sha256"]:
        raise SystemExit("the two runs do not use the same passage file")


def report(run_a: Path, run_b: Path) -> str:
    same_passage(run_a, run_b)
    a, b = load(run_a), load(run_b)
    diff = changed(a, b)
    s = summary(a, b)
    name_a, name_b = tool(run_a), tool(run_b)
    lines = [
        "# Comparison",
        "",
        f"`{run_a.name}` ({name_a}) against `{run_b.name}` ({name_b}), from the two `results.csv` files.",
        "",
        f"- Cases: {s['cases']}",
        f"- Cases with a different edit distance: {s['changed']}",
        f"- Of those, fewer errors with {name_b}: {s['fewer_errors']}",
        f"- Of those, more errors with {name_b}: {s['more_errors']}",
        f"- Edit distance summed over all cases: {s['total_errors'][0]} to {s['total_errors'][1]}",  # type: ignore[index]
        f"- Largest change in character accuracy: {s['largest_change_points']:.2f} percentage points",
        f"- Cases that crossed the {SURVIVES:.0%} pass mark: {len(s['crossed_pass_mark'])}",  # type: ignore[arg-type]
        f"- Smallest passing sizes that changed: {len(s['smallest_passing_size_changed'])}",  # type: ignore[arg-type]
        "",
        "## Changed cases per size",
        "",
        "Each cell is the number of fonts, out of " + str(len({k[0] for k in a})) + ", whose edit distance changed.",
        "",
        "| Size | " + " | ".join(m.name for m in MODES) + " |",
        "|---|" + "---|" * len(MODES),
    ]
    for size in sorted({k[1] for k in a}):
        lines.append(f"| {size} pt | " + " | ".join(str(sum(1 for k, _, _ in diff if k[1] == size and k[2] == m.name)) for m in MODES) + " |")
    lines.append("| All sizes | " + " | ".join(str(s["changed_by_mode"][m.name]) for m in MODES) + " |")  # type: ignore[index]
    lines += [
        "",
        "## Every changed case",
        "",
        f"Edit distance and character accuracy in percent, {name_a} first.",
        "",
        "| Mode | Size | Font | Edit distance | Accuracy |",
        "|---|---|---|---|---|",
    ]
    order = {m.name: i for i, m in enumerate(MODES)}
    for k, x, y in sorted(diff, key=lambda d: (order[d[0][2]], d[0][1])):
        lines.append(f"| {k[2]} | {k[1]} pt | {k[0]} | {x} to {y} | {float(a[k]['char_accuracy']) * 100:.2f} to {float(b[k]['char_accuracy']) * 100:.2f} |")
    return "\n".join(lines) + "\n"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("first", type=Path)
    ap.add_argument("second", type=Path)
    ap.add_argument("--out", type=Path)
    args = ap.parse_args()
    text = report(args.first, args.second)
    if args.out:
        args.out.write_text(text)
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
