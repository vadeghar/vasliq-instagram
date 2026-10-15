"""Publish queued posts that are approved AND due (times are IST). Runs every 30 min on GitHub.
Use --dry-run to preview."""
import sys, json, datetime as dt
from zoneinfo import ZoneInfo
from ig_api import load_env, publish, HERE, IGError

IST = ZoneInfo("Asia/Kolkata")
QUEUE, LOG = HERE / "queue.json", HERE / "post_log.txt"
dry = "--dry-run" in sys.argv

items = json.loads(QUEUE.read_text(encoding="utf-8"))
now = dt.datetime.now(IST).replace(tzinfo=None)
env = None
for it in items:
    if it.get("posted_id") or not it.get("approved"):
        continue
    when = dt.datetime.strptime(it["publish_at"], "%Y-%m-%d %H:%M")
    if when > now:
        continue
    if now - when > dt.timedelta(hours=12):
        print(f"[skip] {it['id']} is >12h overdue; update publish_at to post it.")
        continue
    if dry:
        print(f"[dry-run] would post {it['id']} ({it['type']})"); continue
    env = env or load_env()
    try:
        pid, link = publish(env, it["type"], it["media"], it.get("caption", ""))
        it.update(posted_id=pid, permalink=link, posted_at=dt.datetime.now(IST).strftime("%Y-%m-%d %H:%M"))
        it.pop("last_error", None)
        msg = f"{it['posted_at']} POSTED {it['id']} {link}"
    except IGError as e:
        it["last_error"] = str(e)
        msg = f"{now:%Y-%m-%d %H:%M} ERROR {it['id']}: {e}"
    print(msg)
    with LOG.open("a", encoding="utf-8") as f:
        f.write(msg + "\n")
    QUEUE.write_text(json.dumps(items, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

print(f"Now (IST): {now:%Y-%m-%d %H:%M}")
for i in items:
    if not i.get("posted_id"):
        print(f"  pending: {i['publish_at']}  {i['id']}  {'approved' if i.get('approved') else 'NOT approved'}")
