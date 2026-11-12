<p align="center">
  <a href="https://faxforagents.com"><img src="https://faxforagents.com/brand/logo-512.png" width="88" alt="Fax for Agents"></a>
</p>

<h1 align="center">fax-legibility-bench</h1>

<p align="center">How small can text be before OCR loses it at fax resolution? A reproducible test from <a href="https://faxforagents.com">Fax for Agents</a>.</p>

<p align="center">
  <a href="https://faxforagents.com">Website</a> ·
  <a href="https://faxforagents.com/blog/smallest-font-that-survives-a-fax/">Results post</a> ·
  <a href="https://faxforagents.com/docs/">Docs</a> ·
  <a href="https://faxforagents.com/docs/send-fax/">Send a fax</a> ·
  <a href="https://app.faxforagents.com">Dashboard</a> ·
  <a href="https://faxforagents.com/pricing/">Pricing</a> ·
  <a href="https://faxforagents.com/changelog/">Changelog</a> ·
  <a href="https://faxforagents.com/affiliates/">Affiliate program</a>
</p>

<div align="center">

[![MIT](https://img.shields.io/badge/licence-MIT-1f6feb)](LICENSE)

</div>

The bench sets one public-domain passage at 4 to 16 pt in four open fonts. Each page becomes a 1-bit
image at the two ITU-T T.4 fax resolutions. Tesseract reads every image, and the bench writes character
accuracy per size, font and mode.

It is a simulation of the page image. No number is dialled, no modem, line or carrier is involved, and
nothing is printed. Read the numbers as a best case.

```sh
uv sync
uv run python bench.py
```

## Results of 2026-11-08

From [`results/results.md`](results/results.md). Every font read at 98% or better from 7 pt at
standard resolution, and from 6 pt at fine resolution. At 5 pt standard the scores fell to between
31.56% and 95.84%.

| Font | Smallest passing size, standard | Smallest passing size, fine | 300 dpi gray control |
|---|---|---|---|
| Liberation Serif | 6 pt | 6 pt | 4 pt |
| Liberation Sans | 7 pt | 5 pt | 4 pt |
| DejaVu Sans | 6 pt | 5 pt | 4 pt |
| Noto Sans | 6 pt | 5 pt | 4 pt |

A size passes when it and every larger size tested reach 98% character accuracy. The full tables, the
OCR text of all 156 cases and the tool versions are in [`results/`](results/). A repeat of the 6
to 16 pt sizes with the same Tesseract gave the same numbers.

## Tesseract 5.5.4 run, 2026-11-12

Tesseract 5.5.4 was released on 2026-10-28. This run repeats all 156 cases with it. The results are in
[`results-tesseract-5.5.4/`](results-tesseract-5.5.4/), beside the first run.

The smallest passing size is the same for every font in every mode, so the table above holds for both
versions. No case crossed the 98% mark in either direction.

The scores moved a little. From [`comparison.md`](results-tesseract-5.5.4/comparison.md):

| | Standard | Fine | 300 dpi gray control | All |
|---|---|---|---|---|
| Cases | 52 | 52 | 52 | 156 |
| Cases with a different edit distance | 22 | 16 | 3 | 41 |

Of the 41 changed cases, 5.5.4 made fewer errors in 23 and more in 18. It is not a net gain: the edit
distance summed over all cases went from 3,732 to 3,748. The largest change was 1.17
percentage points, for Liberation Sans at 4 pt standard (63.20% to 62.03%). From 7 pt up, no case changed
by more than 2 characters out of 1,201. At 5 pt standard the scores now run from 31.72% to 96.25%.

What ran:

- Tesseract 5.5.4, built from the `5.5.4` tag (commit `7e548e6`) by the [`Dockerfile`](Dockerfile) on
  Ubuntu 24.04 and linked to Leptonica 1.82.0.
- The same `eng.traineddata` as the first run. Its sha256 starts `7d4322bd` in both `environment.json`
  files. In the image it comes from Ubuntu's `tesseract-ocr-eng` 4.1.0-2.
- The same Typst 0.15.1, Ghostscript 10.02.1, font files and settings. The sample images match byte for byte.
- [`versions.txt`](results-tesseract-5.5.4/versions.txt) holds the output of `tesseract --version` and the package versions.

Two things differ besides the Tesseract version. The first run used the 5.3.4 package of Ubuntu 24.04 on
the test machine. This one used a source build in a container. Python went from 3.14.8 to 3.14.10. The
control below shows that neither changed a result.

The commands:

```sh
docker build --build-arg TESSERACT=5.5.4 -t fax-legibility-bench:5.5.4 .
mkdir -p results-tesseract-5.5.4
docker run --rm -u "$(id -u):$(id -g)" -v "$PWD/results-tesseract-5.5.4:/out" fax-legibility-bench:5.5.4 --out /out
docker run --rm --entrypoint /bench/versions.sh fax-legibility-bench:5.5.4 > results-tesseract-5.5.4/versions.txt
uv run python compare.py results results-tesseract-5.5.4 --out results-tesseract-5.5.4/comparison.md
```

The control is the same build with `--build-arg TESSERACT=5.3.4`. It wrote a `results.csv` and OCR text
that match the first run byte for byte, so the differences come from the Tesseract version.
[`control-5.3.4/`](results-tesseract-5.5.4/control-5.3.4/) holds its `versions.txt` and the sha256 of
its `results.csv`, OCR text and sample images. To check them against the first run:

```sh
cd results && sha256sum -c ../results-tesseract-5.5.4/control-5.3.4/SHA256SUMS
```

## Method

1. Passage: The opening of Chapter I of *Pride and Prejudice* by Jane Austen, Project Gutenberg
   eBook 1342. [`text/SOURCE.md`](text/SOURCE.md) gives the file, its hash and the two edits. It is
   1,201 characters after whitespace is collapsed and has no digits.
2. Layout: [Typst](https://typst.app/) sets it on US Letter with 1 inch margins, hyphenation off,
   at every whole size from 4 to 16 pt. Typst gets the four font files and no system fonts, with fallback off.
3. Fonts: Liberation Serif and Liberation Sans 2.1.5, DejaVu Sans 2.37 and Noto Sans from Ubuntu's
   fonts-noto-core 20201225. Those were installed on the test machine. `environment.json` records each
   file and its sha256.
4. Raster: Ghostscript `pngmono` writes 1-bit pages with no anti-aliasing. Standard is 204 x 98 dpi
   and fine is 204 x 196 dpi. Rows are then repeated, nearest neighbour, until pixels are square at
   204 dpi: two or three times each at standard, once or twice at fine. That is how a printed fax shows each scan line. The control is 300 dpi 8-bit gray.
5. OCR: Tesseract 5.3.4 in the first run and 5.5.4 in the run of 2026-11-12, English model, `--psm 3 --dpi 204` (300 for the control),
   `OMP_THREAD_LIMIT=1`.
6. Score: Both texts are NFKC-normalised, curly quotes and dashes are folded to plain ones and
   whitespace runs become one space. Case and punctuation count. Accuracy is 1 minus the Levenshtein
   distance over the passage length, floored at 0. The 98% pass mark was set before the first run.

The brief was 6 to 16 pt. A trial run read nearly everything at 6 pt, so 4 and 5 pt were added to show
where reading breaks down.

## Limits

- One passage of English prose with no digits. Real faxes are often forms, tables and numbers.
- One OCR engine with its default layout analysis. Below 6 pt it splits and reorders some lines, and the
  edit distance counts those as errors. That is why Liberation Sans scores lower at 5 pt standard
  (31.56% in the first run) than at 4 pt (63.20%).
- No scanner, paper, phone line, error correction or receiving printer. Each of those adds noise.
- The T.4 scan line is 1728 dots on 215 mm. A Letter page at 204 dpi is 1734 dots wide, so the bench
  keeps 6 dots more than a fax would. They fall in the margin.
- OCR is not a person. Most errors from 10 pt up are a capital I read as `|` and a `k` read as `K`, which
  a reader would not make.

## Requirements

Python 3.12 or later with [uv](https://docs.astral.sh/uv/), Typst 0.15 or later, Ghostscript,
Tesseract 5 with the `eng` model, fontconfig and the four fonts. On Ubuntu 24.04:

```sh
sudo apt install ghostscript tesseract-ocr tesseract-ocr-eng fonts-liberation fonts-dejavu-core fonts-noto-core
```

Typst ships as one static binary from its [releases page](https://github.com/typst/typst/releases).
`uv run python bench.py --faces "DejaVu Sans" --sizes 6-8` runs a subset. `uv run pytest` checks the
scoring and the comparison. The [`Dockerfile`](Dockerfile) builds one Tesseract release from source with the rest of the tools.

## Sending a page as a fax

The bench sends nothing. The [send fax docs](https://faxforagents.com/docs/send-fax/) show how to
send a PDF as a fax from code.

Fax for Agents is a fax API, a
hosted MCP server and SDKs for AI agents that send and receive faxes. It is made by JSB Holdings LLC.

## Citing

GitHub's "Cite this repository" button reads [`CITATION.cff`](CITATION.cff). The same entry in BibTeX:

```bibtex
@misc{faxlegibilitybench2026,
author = {JSB Holdings LLC},
month = {11},
title = {fax-legibility-bench},
url = {https://faxforagents.com/blog/smallest-font-that-survives-a-fax/},
year = {2026}
}
```

Each set of numbers belongs to one run. Give the run date and the Tesseract version when you quote them.
The runs are 2026-11-08 with 5.3.4 and 2026-11-12 with 5.5.4.

## Licence

MIT, see [LICENSE](LICENSE). The passage is in the public domain in the United States.
