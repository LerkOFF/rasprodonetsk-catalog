#!/bin/sh
# Обновить каталог: дозабрать новые посты, пересобрать сайт.
cd "$(dirname "$0")" || exit 1
python3 -I scrape.py --new && python3 build.py 30
