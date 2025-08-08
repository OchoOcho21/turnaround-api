#!/usr/bin/env bash
# build.sh
pip install -r requirements.txt
python -m playwright install
python -m playwright install-deps