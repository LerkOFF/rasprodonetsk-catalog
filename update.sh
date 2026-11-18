#!/bin/sh
# Обновить каталог: дозабрать новые посты, проверить удалённые, пересобрать сайт.
# Свежие 3 дня проверяем при каждом запуске, весь месяц не чаще раза в час.
cd "$(dirname "$0")" || exit 1
python3 -I scrape.py --new
python3 -I verify.py 3
STAMP=data/verify_full.stamp
if [ ! -f "$STAMP" ] || [ -n "$(find "$STAMP" -mmin +55)" ]; then
  python3 -I verify.py 31 && touch "$STAMP"
fi
python3 build.py 30
