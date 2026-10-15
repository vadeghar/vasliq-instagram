"""Renew the long-lived token (~60 days). On GitHub it writes the new token to $TOKEN_OUT
(the workflow saves it back into the IG_ACCESS_TOKEN secret)."""
import os
from ig_api import load_env, call

env = load_env()
d = call("GET", "https://graph.instagram.com/refresh_access_token", env["IG_ACCESS_TOKEN"],
         grant_type="ig_refresh_token")
out = os.environ.get("TOKEN_OUT")
if out:
    print(f"::add-mask::{d['access_token']}")
    with open(out, "w") as f:
        f.write(d["access_token"])
print(f"Token refreshed. Valid for {int(d.get('expires_in', 0)) // 86400} days.")
