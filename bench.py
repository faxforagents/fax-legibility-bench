"""Fax legibility bench.

Lays out one public-domain passage at 4 to 16 pt in four open faces, rasterises each page to 1-bit at the two
ITU-T T.4 resolutions (standard 204 x 98 dpi, fine 204 x 196 dpi) plus a 300 dpi grayscale control, runs
Tesseract on every image and writes character accuracy per face, size and mode.

This is a simulation of the page image only. Nothing is dialled, no modem or line is involved, and no
carrier sees any of it. See README.md for the method and its limits.

Usage: uv run python bench.py [--out results] [--faces "Liberation Serif,..."] [--sizes 4-16]
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import hashlib
import json
import os
import platform
import shutil
import subprocess
import sys
import tempfile
import unicodedata
from dataclasses import dataclass
from pathlib import Path

from PIL import Image
from rapidfuzz.distance import Levenshtein

ROOT = Path(__file__).resolve().parent
PASSAGE = ROOT / "text" / "pride-and-prejudice-ch1.txt"

FACES = ["Liberation Serif", "Liberation Sans", "DejaVu Sans", "Noto Sans"]
# The brief was 6 to 16 pt. 4 and 5 pt were added after a trial run read nearly everything at 6 pt, to show
# where reading breaks down.
SIZES = list(range(4, 17))
SAMPLE_FACES = ("Liberation Serif", "Liberation Sans")
SAMPLE_SIZES = (5, 7, 10)

# A size "survives" a mode when OCR reads at least this share of characters correctly. Fixed before the first run.
SURVIVES = 0.98

# T.4 resolutions. Horizontal is 1728 dots on 215 mm, which rounds to 204 dpi; vertical is 3.85 or 7.7 lines/mm.
@dataclass(frozen=True)
class Mode:
    name: str
    x_dpi: int
    y_dpi: int
    one_bit: bool


MODES = [
    Mode("standard", 204, 98, True),
    Mode("fine", 204, 196, True),
    Mode("control-300-gray", 300, 300, False),
]

# Characters the comparison treats as equal. Tesseract often returns straight quotes for curly ones; the bench
# measures legibility, not typographic fidelity, so both sides are folded the same way before comparing.
FOLD = str.maketrans({
    "‘": "'", "’": "'", "‚": "'", "‛": "'",
    "“": '"', "”": '"', "„": '"',
    "‐": "-", "‑": "-", "–": "-", "—": "-",
    " ": " ",
})


def normalise(text: str) -> str:
    """NFKC, fold quotes and dashes, collapse every whitespace run to one space. Case and punctuation still count."""
    text = unicodedata.normalize("NFKC", text).translate(FOLD).replace("…", "...")
    return " ".join(text.split())


def char_accuracy(truth: str, ocr: str) -> tuple[float, int, int]:
    """Return (accuracy, edit distance, truth length) after normalising both sides. Accuracy is clamped at 0."""
    t, o = normalise(truth), normalise(ocr)
    if not t:
        raise ValueError("empty ground truth")
    dist = Levenshtein.distance(t, o)
    return max(0.0, 1.0 - dist / len(t)), dist, len(t)


def paragraphs(text: str) -> list[str]:
    """Blank-line separated paragraphs, each with its hard line breaks turned into spaces."""
    return [" ".join(p.split()) for p in text.split("\n\n") if p.strip()]


def run(cmd: list[str], **kw: object) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, capture_output=True, text=True, **kw)  # type: ignore[call-overload]


def tool_version(cmd: list[str]) -> str:
    out = run(cmd)
    return (out.stdout or out.stderr).strip().splitlines()[0]


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def font_file(face: str) -> Path:
    path = run(["fc-match", "-f", "%{file}", f"{face}:style=Regular"]).stdout.strip()
    family = run(["fc-match", "-f", "%{family[0]}", f"{face}:style=Regular"]).stdout.strip()
    if family != face:
        raise SystemExit(f"{face} is not installed (fontconfig offered {family}). Install it or drop it with --faces.")
    return Path(path)


TYP = """#let paras = sys.inputs.at("text").split("\\n\\n")
#set page(paper: "us-letter", margin: 1in)
#set text(font: sys.inputs.at("face"), size: float(sys.inputs.at("size")) * 1pt, lang: "en", hyphenate: false, fallback: false)
#set par(justify: false)
#for p in paras [#p #parbreak()]
"""


def render_pdf(work: Path, fonts: Path, face: str, size: int, text: str) -> Path:
    src = work / "page.typ"
    src.write_text(TYP)
    pdf = work / f"{face.replace(' ', '-')}-{size}.pdf"
    run([
        "typst", "compile", "--root", str(work), "--font-path", str(fonts), "--ignore-system-fonts",
        "--input", f"face={face}", "--input", f"size={size}", "--input", "text=" + "\n\n".join(paragraphs(text)),
        str(src), str(pdf),
    ])
    return pdf


def rasterise(pdf: Path, mode: Mode, out_dir: Path) -> list[Path]:
    """Ghostscript straight to 1-bit (pngmono, no anti-aliasing) or to 8-bit gray for the control."""
    device = ["-sDEVICE=pngmono"] if mode.one_bit else ["-sDEVICE=pnggray", "-dTextAlphaBits=4", "-dGraphicsAlphaBits=4"]
    pattern = out_dir / f"{pdf.stem}-{mode.name}-%d.png"
    run(["gs", "-q", "-dSAFER", "-dBATCH", "-dNOPAUSE", *device, f"-r{mode.x_dpi}x{mode.y_dpi}", f"-sOutputFile={pattern}", str(pdf)])
    pages = sorted(out_dir.glob(f"{pdf.stem}-{mode.name}-*.png"), key=lambda p: int(p.stem.rsplit("-", 1)[1]))
    if not pages:
        raise RuntimeError(f"ghostscript wrote no page for {pdf.name} {mode.name}")
    return pages


def square_pixels(png: Path, mode: Mode) -> Path:
    """Stretch rows so pixels are square at the horizontal resolution, as a receiver prints each scan line.

    Nearest neighbour only: each 1-bit scan line is repeated, never smoothed, so OCR sees what a printed fax
    shows. The control is already square and is passed through.
    """
    if mode.x_dpi == mode.y_dpi:
        return png
    with Image.open(png) as im:
        w, h = im.size
        tall = im.resize((w, round(h * mode.x_dpi / mode.y_dpi)), Image.Resampling.NEAREST)
        out = png.with_name(png.stem + "-sq.png")
        tall.save(out, dpi=(mode.x_dpi, mode.x_dpi))
    return out


def ocr(png: Path, dpi: int) -> str:
    env = {**os.environ, "OMP_THREAD_LIMIT": "1"}
    return run(["tesseract", str(png), "stdout", "--dpi", str(dpi), "--psm", "3", "-l", "eng"], env=env).stdout


def save_sample(png: Path, dest: Path, dpi: int) -> None:
    """A crop of the first lines (1 in from the top-left corner, 3.5 by 0.45 in) for the README and the post."""
    with Image.open(png) as im:
        box = (dpi, dpi - 4, dpi + int(3.5 * dpi), dpi + int(0.45 * dpi))
        im.crop(box).save(dest, dpi=(dpi, dpi), optimize=True)


def parse_sizes(spec: str) -> list[int]:
    if "-" in spec:
        lo, hi = (int(x) for x in spec.split("-", 1))
        return list(range(lo, hi + 1))
    return [int(x) for x in spec.split(",")]


def smallest_surviving(rows: list[dict[str, object]], face: str, mode: str) -> int | None:
    """Smallest size from which this and every larger tested size reach SURVIVES."""
    sizes = sorted((int(r["size_pt"]), float(r["char_accuracy"])) for r in rows if r["face"] == face and r["mode"] == mode)  # type: ignore[arg-type]
    best: int | None = None
    for size, acc in reversed(sizes):
        if acc < SURVIVES:
            break
        best = size
    return best


def write_markdown(rows: list[dict[str, object]], faces: list[str], sizes: list[int], env: dict[str, object], path: Path) -> None:
    acc = {(r["face"], int(r["size_pt"]), r["mode"]): float(r["char_accuracy"]) for r in rows}  # type: ignore[arg-type]
    lines = [
        "# Results",
        "",
        f"Run on {env['run_date']} with {env['typst']}, {env['ghostscript']}, {env['tesseract']}. "
        f"Passage: {env['passage_chars']} characters from {env['passage_source']}. "
        "Character accuracy is 1 minus the Levenshtein distance divided by the passage length, after the "
        "normalisation in bench.py. Simulation only: no fax call, line or carrier was involved.",
        "",
        f"## Smallest size at {SURVIVES:.0%} or better",
        "",
        "The smallest size from which that size and every larger tested size read at the threshold.",
        "",
        "| Face | " + " | ".join(m.name for m in MODES) + " |",
        "|---|" + "---|" * len(MODES),
    ]
    for face in faces:
        cells = []
        for m in MODES:
            s = smallest_surviving(rows, face, m.name)
            cells.append(f"{s} pt" if s is not None else "none tested")
        lines.append(f"| {face} | " + " | ".join(cells) + " |")
    for m in MODES:
        label = f"{m.name} ({m.x_dpi} x {m.y_dpi} dpi, {'1-bit' if m.one_bit else '8-bit gray'})"
        lines += ["", f"## {label}", "", "Character accuracy, percent.", "", "| Size | " + " | ".join(faces) + " |", "|---|" + "---|" * len(faces)]
        for size in sizes:
            lines.append(f"| {size} pt | " + " | ".join(f"{acc[(f, size, m.name)] * 100:.2f}" for f in faces) + " |")
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    ap.add_argument("--out", type=Path, default=ROOT / "results")
    ap.add_argument("--faces", default=",".join(FACES))
    ap.add_argument("--sizes", default=f"{SIZES[0]}-{SIZES[-1]}")
    args = ap.parse_args()
    faces = [f.strip() for f in args.faces.split(",") if f.strip()]
    sizes = parse_sizes(args.sizes)
    for tool in ("typst", "gs", "tesseract", "fc-match"):
        if shutil.which(tool) is None:
            raise SystemExit(f"{tool} not found on PATH")

    truth = PASSAGE.read_text(encoding="utf-8")
    out: Path = args.out
    (out / "ocr").mkdir(parents=True, exist_ok=True)
    (out / "samples").mkdir(parents=True, exist_ok=True)

    tessdata = run(["tesseract", "--list-langs"]).stdout.splitlines()[0]
    env: dict[str, object] = {
        "run_date": dt.datetime.now(dt.timezone.utc).strftime("%Y-%m-%d"),
        "python": platform.python_version(),
        "os": platform.platform(),
        "typst": tool_version(["typst", "--version"]),
        "ghostscript": "Ghostscript " + tool_version(["gs", "--version"]),
        "tesseract": tool_version(["tesseract", "--version"]),
        "tesseract_model": "eng.traineddata",
        "tesseract_args": "--psm 3 -l eng --dpi <x_dpi>, OMP_THREAD_LIMIT=1",
        "passage_file": str(PASSAGE.relative_to(ROOT)),
        "passage_sha256": sha256(PASSAGE),
        "passage_chars": len(normalise(truth)),
        "passage_source": "Project Gutenberg eBook #1342, Pride and Prejudice by Jane Austen, Chapter I (text/SOURCE.md)",
        "survives_threshold": SURVIVES,
        "modes": [m.__dict__ for m in MODES],
        "fonts": {},
    }
    traineddata = Path(tessdata.split('"')[1]) / "eng.traineddata" if '"' in tessdata else None
    if traineddata and traineddata.exists():
        env["eng_traineddata_sha256"] = sha256(traineddata)

    rows: list[dict[str, object]] = []
    with tempfile.TemporaryDirectory(prefix="flb-") as tmp:
        work = Path(tmp)
        fonts = work / "fonts"
        fonts.mkdir()
        for face in faces:
            src = font_file(face)
            shutil.copy(src, fonts / src.name)
            version = run(["fc-query", "-f", "%{fontversion}", str(src)]).stdout.strip()
            env["fonts"][face] = {"file": str(src), "sha256": sha256(src), "fontversion": version}  # type: ignore[index]
        for face in faces:
            for size in sizes:
                pdf = render_pdf(work, fonts, face, size, truth)
                for mode in MODES:
                    pages = rasterise(pdf, mode, work)
                    text = []
                    for i, png in enumerate(pages):
                        sq = square_pixels(png, mode)
                        text.append(ocr(sq, mode.x_dpi))
                        if i == 0 and face in SAMPLE_FACES and size in SAMPLE_SIZES and mode.one_bit:
                            save_sample(sq, out / "samples" / f"{face.replace(' ', '-').lower()}-{size}pt-{mode.name}.png", mode.x_dpi)
                    joined = "\n".join(text)
                    stem = f"{face.replace(' ', '-').lower()}-{size}pt-{mode.name}"
                    (out / "ocr" / f"{stem}.txt").write_text(joined, encoding="utf-8")
                    acc, dist, n = char_accuracy(truth, joined)
                    rows.append({
                        "face": face, "size_pt": size, "mode": mode.name, "x_dpi": mode.x_dpi, "y_dpi": mode.y_dpi,
                        "bits": 1 if mode.one_bit else 8, "pages": len(pages), "truth_chars": n, "edit_distance": dist,
                        "char_accuracy": f"{acc:.4f}",
                    })
                    print(f"{face:17} {size:2d} pt {mode.name:17} {acc * 100:6.2f}%", flush=True)

    with (out / "results.csv").open("w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
        w.writeheader()
        w.writerows(rows)
    write_markdown(rows, faces, sizes, env, out / "results.md")
    (out / "environment.json").write_text(json.dumps(env, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
