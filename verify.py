"""Проверка, какие посты ещё есть в канале. Удалённый пост считаем снятым с продажи (скорее всего продан).

Запуск: python3 -I verify.py <дней>
Обходит превью канала от свежих постов назад на N дней, сверяет с data/posts.jsonl и обновляет data/gone.json
({id поста: время, когда заметили пропажу}). Если выкачка где-то сбилась, ничего не меняет.
"""
import json, re, subprocess, sys, time, datetime, os

CHANNEL = "rasprodonetsk"
DAYS = int(sys.argv[1]) if len(sys.argv) > 1 else 3
POSTS, GONE = "data/posts.jsonl", "data/gone.json"

def fetch(before):
    url = f"https://t.me/s/{CHANNEL}" + (f"?before={before}" if before else "")
    for _ in range(4):
        r = subprocess.run(["curl", "-sL", "-m", "30", url], capture_output=True, text=True).stdout
        if "tgme_widget_message_wrap" in r:
            return r
        time.sleep(2)
    return None

def ids_dates(page):
    out = []
    for b in re.split(r'(?=<div class="tgme_widget_message_wrap)', page):
        m = re.search(r'data-post="%s/(\d+)"' % CHANNEL, b)
        d = re.search(r'datetime="([^"]+)"', b)
        if m and d:
            out.append((int(m.group(1)), d.group(1)))
    return out

known = {}
for line in open(POSTS, encoding="utf8"):
    p = json.loads(line); known[p["id"]] = p["date"]
now = datetime.datetime.now(datetime.timezone.utc)
cutoff = now - datetime.timedelta(days=DAYS)

present, before, lo = set(), None, None
while True:
    page = fetch(before)
    if page is None:
        print("сбой выкачки, gone.json не менял"); sys.exit(1)
    rows = ids_dates(page)
    if not rows:
        print("пустая страница, gone.json не менял"); sys.exit(1)
    for i, d in rows:
        present.add(i)
    lo = min(i for i, _ in rows)
    oldest = datetime.datetime.fromisoformat(min(d for _, d in rows))
    if oldest < cutoff or lo <= 1:
        break
    before = lo
    time.sleep(0.4)

gone = json.load(open(GONE)) if os.path.exists(GONE) else {}
stamp = now.isoformat(timespec="seconds")
added = 0
for i in known:
    if i >= lo and i not in present and str(i) not in gone:
        gone[str(i)] = stamp; added += 1
back = [k for k in list(gone) if int(k) in present]   # пост вернулся
for k in back: del gone[k]
json.dump(gone, open(GONE, "w"))
print(f"проверено с id {lo}, в канале {len(present)}, новых снятых {added}, вернулось {len(back)}, всего снятых {len(gone)}")
