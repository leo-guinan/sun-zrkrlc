#!/usr/bin/env python3
from __future__ import annotations
import datetime as dt, json, re, urllib.parse, urllib.request
from pathlib import Path
API_DOC_URL='https://raw.githubusercontent.com/TheExGenesis/community-archive/main/docs/api-doc.md'
SUPABASE_URL='https://fabxmporizzqflnftavs.supabase.co'
def fetch_anon_key():
    text=urllib.request.urlopen(API_DOC_URL,timeout=30).read().decode()
    m=re.search(r'eyJ[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+\.[A-Za-z0-9_-]+',text)
    if not m: raise RuntimeError('Community Archive anon key not found in upstream docs')
    return m.group(0)
def get_json(path, params):
    k=fetch_anon_key()
    url=SUPABASE_URL+path+'?'+urllib.parse.urlencode(params, doseq=True)
    req=urllib.request.Request(url,headers={'apikey':k,'Authorization':'Bearer '+k,'Accept':'application/json'})
    with urllib.request.urlopen(req,timeout=60) as resp: return json.loads(resp.read().decode())
def username_from_readme():
    txt=Path('README.md').read_text()
    m=re.search(r'@([A-Za-z0-9_]+)',txt)
    if not m: raise RuntimeError('Could not infer username from README')
    return m.group(1).lower()
def read_jsonl(p):
    return [json.loads(l) for l in Path(p).read_text().splitlines() if l.strip()] if Path(p).exists() else []
def write_jsonl(p, rows):
    Path(p).parent.mkdir(parents=True,exist_ok=True)
    Path(p).write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in rows)+('\n' if rows else ''))
def norm_api(row, username, fetched_at):
    tid=str(row.get('tweet_id') or row.get('id') or row.get('id_str') or '')
    text=row.get('full_text') or row.get('text') or row.get('body') or ''
    created=row.get('created_at') or row.get('createdAt')
    return {'id':tid,'kind':'tweet','username':username,'created_at':created,'text':text,'url':f'https://x.com/{username}/status/{tid}' if tid else '', 'favorite_count':row.get('favorite_count') or row.get('likes') or 0, 'retweet_count':row.get('retweet_count') or row.get('retweets') or 0, 'source_dataset':'supabase_incremental','api_fetched_at':fetched_at,'raw':row}
def main():
    username=username_from_readme(); fetched_at=dt.datetime.now(dt.timezone.utc).isoformat()
    acct=get_json('/rest/v1/account', {'username':'eq.'+username,'select':'account_id,username','limit':1})
    if acct:
        account_id=acct[0]['account_id']
    else:
        meta_path=Path('data/account_meta.json')
        if meta_path.exists():
            account=json.loads(meta_path.read_text())
        elif Path('data/archive.json').exists():
            archive=json.loads(Path('data/archive.json').read_text())
            account=(archive.get('account') or [{}])[0].get('account',{})
        else:
            account={}
        account_id=account.get('accountId')
        if not account_id: raise RuntimeError(f'No Supabase account row or archive accountId for {username}')
    archive_rows=read_jsonl('data/archive_posts.jsonl')
    max_created=max([r.get('created_at') or '' for r in archive_rows], default='')
    params={'account_id':'eq.'+str(account_id),'select':'*','order':'created_at.asc','limit':1000}
    if max_created: params['created_at']='gt.'+max_created
    rows=[]; offset=0
    while True:
        params['offset']=offset
        page=get_json('/rest/v1/tweets', params)
        if not page: break
        rows.extend(norm_api(r,username,fetched_at) for r in page if (r.get('full_text') or r.get('text') or r.get('body')))
        if len(page)<1000: break
        offset += len(page)
    dump=f"data/updates/{fetched_at.replace(':','').replace('+','Z')}.tweets.jsonl"
    write_jsonl(dump, rows)
    merged={r['id']:r for r in archive_rows if r.get('id')}
    for r in rows:
        if r.get('id'): merged[r['id']]=r
    write_jsonl('data/merged_posts.jsonl', sorted(merged.values(), key=lambda r:(r.get('created_at') or '', r.get('id') or '')))
    print(json.dumps({'username':username,'account_id':account_id,'archive_rows':len(archive_rows),'incremental_rows':len(rows),'dump':dump,'merged_rows':len(merged)}, indent=2))
if __name__=='__main__': main()
