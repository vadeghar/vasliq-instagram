"""Shared helpers for the official Instagram API (Instagram Login).
Credentials come from environment variables (GitHub Secrets) or a local .env file."""
import os, time, pathlib, requests

BASE = "https://graph.instagram.com/v23.0"
HERE = pathlib.Path(__file__).resolve().parent
ENV_PATH = HERE / ".env"


def load_env():
    env = {}
    if ENV_PATH.exists():
        for line in ENV_PATH.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                env[k.strip()] = v.strip().strip('"').strip("'")
    for k in ("IG_USER_ID", "IG_ACCESS_TOKEN"):
        if os.environ.get(k):
            env[k] = os.environ[k]
        if not env.get(k):
            raise SystemExit(f"{k} missing (set it as a GitHub secret or in .env)")
    return env


class IGError(Exception):
    pass


def call(method, path, token, **params):
    url = path if path.startswith("http") else f"{BASE}/{path.lstrip('/')}"
    params["access_token"] = token
    r = requests.request(method, url, params=params if method == "GET" else None,
                         data=params if method != "GET" else None, timeout=60)
    try:
        data = r.json()
    except ValueError:
        raise IGError(f"HTTP {r.status_code}: {r.text[:200]}")
    if r.status_code >= 400 or "error" in data:
        err = data.get("error", {})
        raise IGError(f"{err.get('message', data)} (code {err.get('code')})")
    return data


def wait_ready(container_id, token, timeout=600):
    start = time.time()
    while time.time() - start < timeout:
        st = call("GET", container_id, token, fields="status_code").get("status_code")
        if st == "FINISHED":
            return
        if st in ("ERROR", "EXPIRED"):
            raise IGError(f"Container {container_id} failed: {st}")
        time.sleep(10)
    raise IGError("Timed out waiting for media processing")


def publish(env, kind, media, caption=""):
    """kind: image | carousel | reel. media: list of public https URLs."""
    uid, tok = env["IG_USER_ID"], env["IG_ACCESS_TOKEN"]
    if kind == "image":
        c = call("POST", f"{uid}/media", tok, image_url=media[0], caption=caption)["id"]
    elif kind == "reel":
        c = call("POST", f"{uid}/media", tok, media_type="REELS", video_url=media[0],
                 caption=caption, share_to_feed="true")["id"]
    elif kind == "carousel":
        if not 2 <= len(media) <= 10:
            raise IGError("Carousel needs 2-10 items")
        kids = []
        for url in media:
            is_video = url.lower().endswith((".mp4", ".mov"))
            p = dict(is_carousel_item="true")
            p.update(media_type="VIDEO", video_url=url) if is_video else p.update(image_url=url)
            kid = call("POST", f"{uid}/media", tok, **p)["id"]
            if is_video:
                wait_ready(kid, tok)
            kids.append(kid)
        c = call("POST", f"{uid}/media", tok, media_type="CAROUSEL",
                 children=",".join(kids), caption=caption)["id"]
    else:
        raise IGError(f"Unknown kind {kind}")
    wait_ready(c, tok)
    post_id = call("POST", f"{uid}/media_publish", tok, creation_id=c)["id"]
    link = call("GET", post_id, tok, fields="permalink").get("permalink", "")
    return post_id, link
