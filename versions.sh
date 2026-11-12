#!/bin/sh
# Prints what the image holds: the Tesseract build, its source commit, the model file and the Ubuntu packages.
#   docker run --rm --entrypoint /bench/versions.sh fax-legibility-bench:5.5.4 > results-tesseract-5.5.4/versions.txt
set -eu
tesseract --version 2>&1
tesseract --list-langs
echo "source commit $(cat /tesseract-commit.txt)"
sha256sum "$TESSDATA_PREFIX/eng.traineddata"
dpkg-query -W -f '${Package} ${Version}\n' tesseract-ocr-eng liblept5 libleptonica-dev ghostscript fonts-liberation fonts-dejavu-core fonts-noto-core
typst --version
