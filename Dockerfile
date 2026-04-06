# Phase 3: target Python 3.12 (see upgrade-details.md; fallback 3.11 only if install fails).
FROM python:3.12-bookworm

# Google Chrome stable — modern apt keyring (no deprecated apt-key).
# Driver: undetected-chromedriver resolves/downloads a matching chromedriver at runtime;
# do not install a separate binary from chromedriver.storage.googleapis.com (legacy / mismatch risk).
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        ca-certificates \
        curl \
        gnupg \
        wget \
    && wget -q -O - https://dl.google.com/linux/linux_signing_key.pub \
        | gpg --dearmor -o /usr/share/keyrings/google-chrome.gpg \
    && echo "deb [arch=amd64 signed-by=/usr/share/keyrings/google-chrome.gpg] http://dl.google.com/linux/chrome/deb/ stable main" \
        > /etc/apt/sources.list.d/google-chrome.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends google-chrome-stable \
    && rm -rf /var/lib/apt/lists/*

# Headless flow in downloader.py uses --headless only; no Xvfb in this image — omit DISPLAY.

WORKDIR /usr/src/app

COPY . /app
WORKDIR /app

RUN pip install --upgrade pip

RUN pip install -r requirements.txt \
    && pip install -r requirements-dev.txt

# Record runtime versions for upgrade notes (driver comes from uc at runtime).
RUN python --version && google-chrome-stable --version

CMD python main.py
