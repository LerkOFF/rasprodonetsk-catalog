"""Сбор постов публичного канала через превью t.me/s/<канал>. Дописывает data/posts.jsonl, можно прерывать и запускать снова."""
import re, html, json, subprocess, time, sys, os

CHANNEL = "rasprodonetsk"
OUT = "data/posts.jsonl"
STOP_DATE = sys.argv[1] if len(sys.argv) > 1 else "2000-01-01"  # дальше этой даты не идём

def fetch(url):
    for _ in range(4):
        r = subprocess.run(["curl", "-sL", "-m", "30", url], capture_output=True, text=True)
        if r.stdout and "tgme_widget_message_wrap" in r.stdout:
            return r.stdout
        time.sleep(2)
    return ""

def parse(page):
    out = []
    for b in re.split(r'(?=<div class="tgme_widget_message_wrap)', page):
        m = re.search(r'data-post="%s/(\d+)"' % CHANNEL, b)
        if not m:
            continue
        t = re.search(r'tgme_widget_message_text[^>]*>(.*?)</div>', b, re.S)
        txt = re.sub(r'<br/?>', '\n', t.group(1)) if t else ''
        txt = html.unescape(re.sub(r'<[^>]+>', '', txt)).strip()
        d = re.search(r'datetime="([^"]+)"', b)
        photos = re.findall(r"tgme_widget_message_photo_wrap[^>]*background-image:url\('([^']+)'\)", b)
        out.append({"id": int(m.group(1)), "date": d.group(1) if d else "", "text": txt, "photos": photos})
    return out

seen = {}
if os.path.exists(OUT):
    for line in open(OUT, encoding="utf8"):
        p = json.loads(line); seen[p["id"]] = p
NEW = "--new" in sys.argv   # дозабрать свежие посты поверх уже собранных
if NEW: sys.argv.remove("--new"); STOP_DATE = "2000-01-01"
top = max(seen) if seen else 0
before = None if NEW else (min(seen) if seen else None)
f = open(OUT, "a", encoding="utf8")
pages = 0
while True:
    page = fetch(f"https://t.me/s/{CHANNEL}" + (f"?before={before}" if before else ""))
    posts = parse(page)
    if not posts:
        break
    for p in posts:
        if p["id"] not in seen:
            seen[p["id"]] = p
            f.write(json.dumps(p, ensure_ascii=False) + "\n")
    f.flush()
    before = min(p["id"] for p in posts)
    pages += 1
    if pages % 20 == 0:
        print(pages, before, posts[0]["date"][:10], flush=True)
    if before <= 1 or posts[0]["date"][:10] < STOP_DATE or (NEW and before <= top):
        break
    time.sleep(0.4)
print("done", len(seen), "min", min(seen))
