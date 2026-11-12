#!/usr/bin/env bash
# Install headless browser / GL packages for Playwright on GitHub-hosted runners.
# Mirrors resilience patterns from the tests job Qt apt step: never unlink apt/dpkg
# lock files (wait via DPkg::Lock::Timeout), strip broken Google Chrome apt sources,
# retries, and non-fatal last resort.
set -euo pipefail

if ! sudo -n true 2>/dev/null; then
  echo "No passwordless sudo — assuming system deps are pre-installed (self-hosted runner)"
  exit 0
fi

sudo rm -f /etc/apt/sources.list.d/*chrome* /etc/apt/sources.list.d/*google*
# Drop dl.google.com chrome lists that break apt on hosted runners.
sudo sed -i '/dl\.google\.com/d' /etc/apt/sources.list 2>/dev/null || true

APT_READY=false
for attempt in 1 2 3; do
  echo "apt-get update attempt $attempt of 3"
  if sudo env DEBIAN_FRONTEND=noninteractive apt-get -o DPkg::Lock::Timeout=300 update --fix-missing; then
    APT_READY=true
    break
  fi
  sleep 10
done

if [ "$APT_READY" != "true" ]; then
  echo "::warning::apt-get update could not complete; continuing with existing system dependencies"
  exit 0
fi

if apt-cache show libasound2t64 >/dev/null 2>&1; then
  LIBASOUND=libasound2t64
else
  LIBASOUND=libasound2
fi

PACKAGES=(
  libgl1
  libegl1
  libxrandr2
  libxss1
  libxcursor1
  libxcomposite1
  "$LIBASOUND"
  libxi6
  libxtst6
)

APT_INSTALL_OK=false
for attempt in 1 2 3; do
  echo "apt-get install attempt $attempt of 3"
  if sudo env DEBIAN_FRONTEND=noninteractive apt-get -o DPkg::Lock::Timeout=300 install -y \
    --fix-missing --no-install-recommends "${PACKAGES[@]}"; then
    APT_INSTALL_OK=true
    break
  fi
  sleep 10
done

if [ "$APT_INSTALL_OK" != "true" ]; then
  echo "::warning::apt-get install did not complete after 3 attempts; continuing (self-hosted or pre-provisioned runners may still succeed)"
fi
