# One Tesseract release built from its source tag on Ubuntu 24.04, with the bench and its other tools.
# The English model, Leptonica, Ghostscript and the fonts come from Ubuntu packages, as in the first run.
#
#   docker build --build-arg TESSERACT=5.5.4 -t fax-legibility-bench:5.5.4 .
#   mkdir -p results-tesseract-5.5.4
#   docker run --rm -u "$(id -u):$(id -g)" -v "$PWD/results-tesseract-5.5.4:/out" fax-legibility-bench:5.5.4 --out /out
#   docker run --rm --entrypoint /bench/versions.sh fax-legibility-bench:5.5.4 > results-tesseract-5.5.4/versions.txt
# The digest is the ubuntu:24.04 image of 2026-11-12. The apt packages are not pinned, so versions.sh prints them.
FROM ubuntu:24.04@sha256:2198e4c65076e9cb0b3d695219df667c0e3b0072da64ca3c2648aca17dcecaf5

ARG TESSERACT=5.5.4
ARG TYPST=0.15.1
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install -y --no-install-recommends \
        ca-certificates curl xz-utils git build-essential automake libtool pkg-config libleptonica-dev \
        ghostscript tesseract-ocr-eng fontconfig fonts-liberation fonts-dejavu-core fonts-noto-core \
    && rm -rf /var/lib/apt/lists/*

RUN curl -fsSL "https://github.com/typst/typst/releases/download/v${TYPST}/typst-x86_64-unknown-linux-musl.tar.xz" \
    | tar -xJ -C /usr/local/bin --strip-components=1 --wildcards '*/typst'

RUN git clone -q --depth 1 --branch "${TESSERACT}" https://github.com/tesseract-ocr/tesseract.git /src \
    && cd /src && git rev-parse HEAD > /tesseract-commit.txt \
    && ./autogen.sh && ./configure --prefix=/opt/tesseract --disable-doc \
    && make -j"$(nproc)" && make install && rm -rf /src

# The model file is the one Ubuntu's tesseract-ocr-eng package installs.
ENV PATH=/opt/tesseract/bin:$PATH \
    LD_LIBRARY_PATH=/opt/tesseract/lib \
    TESSDATA_PREFIX=/usr/share/tesseract-ocr/5/tessdata \
    UV_PYTHON_INSTALL_DIR=/opt/python \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    UV_CACHE_DIR=/tmp/uv-cache \
    HOME=/tmp

RUN curl -LsSf https://astral.sh/uv/install.sh | env UV_INSTALL_DIR=/usr/local/bin sh

WORKDIR /bench
COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --python 3.14 && chmod -R a+rX /opt/python /opt/venv && rm -rf /tmp/uv-cache
COPY bench.py versions.sh ./
COPY text ./text

ENTRYPOINT ["uv", "run", "--frozen", "--no-sync", "python", "bench.py"]
