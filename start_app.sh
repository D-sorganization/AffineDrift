#!/bin/bash
python3 scripts/sync_frontend_assets.py
python3 -m http.server 8000 --directory docs/ &
