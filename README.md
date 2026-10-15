# Vasliq Instagram – cloud posting (GitHub Actions)

Posts approved items from `queue.json` at their `publish_at` time (IST), even when your PC is off.

## Add a post
1. Upload the image/video to the Netlify site under `/ig/` (JPG for images, MP4 for reels).
2. Edit `queue.json` on GitHub (pencil icon) and add an item:
```json
{
  "id": "unique-name",
  "type": "reel",
  "media": ["https://vasliq.netlify.app/ig/file.mp4"],
  "caption": "Your caption",
  "publish_at": "2026-10-25 20:30",
  "approved": true,
  "posted_id": null
}
```
`type`: `image`, `carousel` (2–10 URLs) or `reel`.

## Check
- Results: `post_log.txt`, and each posted item gets `permalink` in `queue.json`.
- Actions tab → "Post to Instagram" → latest run shows pending posts.
- Run now: Actions → workflow → **Run workflow**.

## Secrets (Settings → Secrets and variables → Actions)
`IG_USER_ID`, `IG_ACCESS_TOKEN`, `GH_PAT` (used only by the weekly token refresh).
