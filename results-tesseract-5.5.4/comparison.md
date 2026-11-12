# Comparison

`results` (tesseract 5.3.4) against `results-tesseract-5.5.4` (tesseract 5.5.4), from the two `results.csv` files.

- Cases: 156
- Cases with a different edit distance: 41
- Of those, fewer errors with tesseract 5.5.4: 23
- Of those, more errors with tesseract 5.5.4: 18
- Edit distance summed over all cases: 3732 to 3748
- Largest change in character accuracy: 1.17 percentage points
- Cases that crossed the 98% pass mark: 0
- Smallest passing sizes that changed: 0

## Changed cases per size

Each cell is the number of fonts, out of 4, whose edit distance changed.

| Size | standard | fine | control-300-gray |
|---|---|---|---|
| 4 pt | 4 | 4 | 0 |
| 5 pt | 3 | 3 | 0 |
| 6 pt | 3 | 1 | 0 |
| 7 pt | 2 | 2 | 0 |
| 8 pt | 2 | 1 | 1 |
| 9 pt | 0 | 0 | 0 |
| 10 pt | 1 | 1 | 0 |
| 11 pt | 2 | 0 | 1 |
| 12 pt | 2 | 1 | 0 |
| 13 pt | 0 | 1 | 1 |
| 14 pt | 1 | 1 | 0 |
| 15 pt | 2 | 1 | 0 |
| 16 pt | 0 | 0 | 0 |
| All sizes | 22 | 16 | 3 |

## Every changed case

Edit distance and character accuracy in percent, tesseract 5.3.4 first.

| Mode | Size | Font | Edit distance | Accuracy |
|---|---|---|---|---|
| standard | 4 pt | Liberation Serif | 636 to 648 | 47.04 to 46.04 |
| standard | 4 pt | Liberation Sans | 442 to 456 | 63.20 to 62.03 |
| standard | 4 pt | DejaVu Sans | 282 to 279 | 76.52 to 76.77 |
| standard | 4 pt | Noto Sans | 424 to 421 | 64.70 to 64.95 |
| standard | 5 pt | Liberation Serif | 291 to 294 | 75.77 to 75.52 |
| standard | 5 pt | Liberation Sans | 822 to 820 | 31.56 to 31.72 |
| standard | 5 pt | Noto Sans | 50 to 45 | 95.84 to 96.25 |
| standard | 6 pt | Liberation Sans | 65 to 61 | 94.59 to 94.92 |
| standard | 6 pt | DejaVu Sans | 13 to 10 | 98.92 to 99.17 |
| standard | 6 pt | Noto Sans | 15 to 16 | 98.75 to 98.67 |
| standard | 7 pt | Liberation Sans | 7 to 5 | 99.42 to 99.58 |
| standard | 7 pt | DejaVu Sans | 4 to 5 | 99.67 to 99.58 |
| standard | 8 pt | DejaVu Sans | 9 to 8 | 99.25 to 99.33 |
| standard | 8 pt | Noto Sans | 11 to 9 | 99.08 to 99.25 |
| standard | 10 pt | Noto Sans | 2 to 1 | 99.83 to 99.92 |
| standard | 11 pt | DejaVu Sans | 2 to 3 | 99.83 to 99.75 |
| standard | 11 pt | Noto Sans | 1 to 0 | 99.92 to 100.00 |
| standard | 12 pt | Liberation Serif | 1 to 0 | 99.92 to 100.00 |
| standard | 12 pt | Noto Sans | 1 to 2 | 99.92 to 99.83 |
| standard | 14 pt | Liberation Sans | 3 to 5 | 99.75 to 99.58 |
| standard | 15 pt | Liberation Serif | 1 to 0 | 99.92 to 100.00 |
| standard | 15 pt | Liberation Sans | 1 to 2 | 99.92 to 99.83 |
| fine | 4 pt | Liberation Serif | 103 to 112 | 91.42 to 90.67 |
| fine | 4 pt | Liberation Sans | 70 to 65 | 94.17 to 94.59 |
| fine | 4 pt | DejaVu Sans | 39 to 38 | 96.75 to 96.84 |
| fine | 4 pt | Noto Sans | 25 to 32 | 97.92 to 97.34 |
| fine | 5 pt | Liberation Serif | 31 to 34 | 97.42 to 97.17 |
| fine | 5 pt | Liberation Sans | 14 to 15 | 98.83 to 98.75 |
| fine | 5 pt | Noto Sans | 8 to 6 | 99.33 to 99.50 |
| fine | 6 pt | Noto Sans | 18 to 16 | 98.50 to 98.67 |
| fine | 7 pt | Liberation Sans | 7 to 6 | 99.42 to 99.50 |
| fine | 7 pt | DejaVu Sans | 1 to 2 | 99.92 to 99.83 |
| fine | 8 pt | Liberation Serif | 3 to 2 | 99.75 to 99.83 |
| fine | 10 pt | Noto Sans | 1 to 2 | 99.92 to 99.83 |
| fine | 12 pt | Noto Sans | 1 to 0 | 99.92 to 100.00 |
| fine | 13 pt | Liberation Sans | 2 to 1 | 99.83 to 99.92 |
| fine | 14 pt | DejaVu Sans | 1 to 0 | 99.92 to 100.00 |
| fine | 15 pt | Liberation Sans | 2 to 1 | 99.83 to 99.92 |
| control-300-gray | 8 pt | Liberation Sans | 1 to 2 | 99.92 to 99.83 |
| control-300-gray | 11 pt | Liberation Sans | 1 to 2 | 99.92 to 99.83 |
| control-300-gray | 13 pt | DejaVu Sans | 1 to 2 | 99.92 to 99.83 |
