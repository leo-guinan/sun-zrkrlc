# @zrkrlc Solar Museum

Community Archive-derived solar-system repository for `@zrkrlc`.

## Files

- `data/archive.json` — raw public Community Archive storage snapshot.
- `data/archive_posts.jsonl` — normalized tweets, note-tweets, and community tweets from the archive.
- `data/updates/` — Supabase incremental update dumps produced by `scripts/update_from_supabase.py`.
- `data/merged_posts.jsonl` — archive plus updates, deduped by post id.
- `sun.json` — visitable proof-of-search map.

## Update

```bash
python3 scripts/update_from_supabase.py
python3 scripts/build_sun.py
```

Boundary: this is public-source archive terrain, not reputation. Raw archive coverage and Supabase freshness are explicit provenance, not magic.
