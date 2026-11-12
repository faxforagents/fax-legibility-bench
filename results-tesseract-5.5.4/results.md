# Results

Run on 2026-11-12 with typst 0.15.1 (9dfd3a08), Ghostscript 10.02.1, tesseract 5.5.4. Passage: 1201 characters from Project Gutenberg eBook #1342, Pride and Prejudice by Jane Austen, Chapter I (text/SOURCE.md). Character accuracy is 1 minus the Levenshtein distance divided by the passage length, after the normalisation in bench.py. Simulation only: no fax call, line or carrier was involved.

## Smallest size at 98% or better

The smallest size from which that size and every larger tested size read at the threshold.

| Face | standard | fine | control-300-gray |
|---|---|---|---|
| Liberation Serif | 6 pt | 6 pt | 4 pt |
| Liberation Sans | 7 pt | 5 pt | 4 pt |
| DejaVu Sans | 6 pt | 5 pt | 4 pt |
| Noto Sans | 6 pt | 5 pt | 4 pt |

## standard (204 x 98 dpi, 1-bit)

Character accuracy, percent.

| Size | Liberation Serif | Liberation Sans | DejaVu Sans | Noto Sans |
|---|---|---|---|---|
| 4 pt | 46.04 | 62.03 | 76.77 | 64.95 |
| 5 pt | 75.52 | 31.72 | 93.26 | 96.25 |
| 6 pt | 99.00 | 94.92 | 99.17 | 98.67 |
| 7 pt | 99.33 | 99.58 | 99.58 | 99.17 |
| 8 pt | 99.67 | 99.75 | 99.33 | 99.25 |
| 9 pt | 99.67 | 99.25 | 99.67 | 99.75 |
| 10 pt | 99.83 | 99.92 | 99.92 | 99.92 |
| 11 pt | 100.00 | 99.83 | 99.75 | 100.00 |
| 12 pt | 100.00 | 99.75 | 99.92 | 99.83 |
| 13 pt | 100.00 | 99.75 | 99.75 | 99.83 |
| 14 pt | 100.00 | 99.58 | 99.75 | 99.92 |
| 15 pt | 100.00 | 99.83 | 99.83 | 99.83 |
| 16 pt | 100.00 | 99.83 | 99.42 | 100.00 |

## fine (204 x 196 dpi, 1-bit)

Character accuracy, percent.

| Size | Liberation Serif | Liberation Sans | DejaVu Sans | Noto Sans |
|---|---|---|---|---|
| 4 pt | 90.67 | 94.59 | 96.84 | 97.34 |
| 5 pt | 97.17 | 98.75 | 98.67 | 99.50 |
| 6 pt | 98.17 | 99.25 | 99.92 | 98.67 |
| 7 pt | 99.67 | 99.50 | 99.83 | 99.75 |
| 8 pt | 99.83 | 99.67 | 99.92 | 99.92 |
| 9 pt | 100.00 | 99.92 | 99.92 | 99.92 |
| 10 pt | 100.00 | 99.92 | 99.92 | 99.83 |
| 11 pt | 100.00 | 99.75 | 99.92 | 99.92 |
| 12 pt | 99.83 | 99.83 | 99.92 | 100.00 |
| 13 pt | 100.00 | 99.92 | 99.92 | 100.00 |
| 14 pt | 100.00 | 99.92 | 100.00 | 100.00 |
| 15 pt | 100.00 | 99.92 | 99.92 | 100.00 |
| 16 pt | 100.00 | 99.92 | 99.83 | 100.00 |

## control-300-gray (300 x 300 dpi, 8-bit gray)

Character accuracy, percent.

| Size | Liberation Serif | Liberation Sans | DejaVu Sans | Noto Sans |
|---|---|---|---|---|
| 4 pt | 99.58 | 98.17 | 99.58 | 99.83 |
| 5 pt | 99.83 | 99.83 | 99.92 | 100.00 |
| 6 pt | 100.00 | 99.92 | 99.92 | 100.00 |
| 7 pt | 100.00 | 99.92 | 99.92 | 100.00 |
| 8 pt | 100.00 | 99.83 | 99.92 | 100.00 |
| 9 pt | 100.00 | 99.92 | 99.92 | 100.00 |
| 10 pt | 99.92 | 99.83 | 99.92 | 100.00 |
| 11 pt | 100.00 | 99.83 | 99.92 | 100.00 |
| 12 pt | 100.00 | 99.83 | 99.92 | 100.00 |
| 13 pt | 100.00 | 99.92 | 99.83 | 100.00 |
| 14 pt | 100.00 | 99.83 | 99.83 | 100.00 |
| 15 pt | 100.00 | 99.92 | 99.92 | 100.00 |
| 16 pt | 100.00 | 99.83 | 99.83 | 100.00 |
