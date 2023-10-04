#!/usr/bin/env bash
set -euo pipefail

echo Test python app
python manage.py test
