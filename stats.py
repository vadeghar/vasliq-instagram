"""Weekly stats: account overview + last 12 posts -> stats/stats_YYYY-MM-DD.csv"""
import csv, datetime as dt
from ig_api import load_env, call, HERE, IGError

env = load_env(); tok, uid = env["IG_ACCESS_TOKEN"], env["IG_USER_ID"]
me = call("GET", "me", tok, fields="username,followers_count,media_count")
print(f"@{me['username']}  followers {me.get('followers_count')}  posts {me.get('media_count')}")
since = int((dt.datetime.now() - dt.timedelta(days=7)).timestamp())
for m in ("reach", "views", "accounts_engaged", "total_interactions", "profile_links_taps"):
    try:
        d = call("GET", f"{uid}/insights", tok, metric=m, period="day", metric_type="total_value", since=since)
        print(f"  7-day {m}: {d['data'][0]['total_value']['value']}")
    except (IGError, KeyError, IndexError):
        print(f"  7-day {m}: n/a")
media = call("GET", f"{uid}/media", tok, limit=12,
             fields="id,caption,media_type,media_product_type,timestamp,permalink,like_count,comments_count").get("data", [])
rows = []
for p in media:
    row = {"date": p["timestamp"][:10], "type": p.get("media_product_type") or p["media_type"],
           "likes": p.get("like_count", 0), "comments": p.get("comments_count", 0),
           "caption": (p.get("caption") or "").split("\n")[0][:50], "link": p.get("permalink")}
    for m in ("reach", "views", "saved", "shares"):
        try:
            row[m] = call("GET", f"{p['id']}/insights", tok, metric=m)["data"][0]["values"][0]["value"]
        except (IGError, KeyError, IndexError):
            row[m] = ""
    rows.append(row)
    print(f"{row['date']} {row['type']:<9} reach {row['reach']!s:>5} views {row['views']!s:>5} likes {row['likes']:>3}  {row['caption']}")
if rows:
    (HERE / "stats").mkdir(exist_ok=True)
    out = HERE / "stats" / f"stats_{dt.date.today()}.csv"
    with out.open("w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0])); w.writeheader(); w.writerows(rows)
    print("Saved", out.name)
