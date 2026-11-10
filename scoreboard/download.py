"""Cache original public files; record retrieval time, hash, URL and failures.

Run python -m scoreboard.download from the repository root.
No credentials, registration bypasses, or fabricated fallback datasets.
"""
import argparse
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import time
import requests

ROOT = Path(__file__).resolve().parents[1]

def fetch(spec, refresh=False):
    path = ROOT / 'data/raw' / spec['file']
    path.parent.mkdir(parents=True, exist_ok=True)
    meta_path = path.with_name(path.name + '.meta.json')
    if path.exists() and meta_path.exists() and not refresh:
        meta = json.loads(meta_path.read_text())
        if hashlib.sha256(path.read_bytes()).hexdigest() != meta['sha256']:
            raise ValueError(f'Cache hash mismatch: {path}')
        return meta
    meta = dict(spec, retrieved_utc=datetime.now(timezone.utc).isoformat())
    for attempt in range(3):
        try:
            r = requests.get(spec['url'], timeout=90, headers={'User-Agent':'AC547-academic-research/1.0'})
            r.raise_for_status()
            if spec['file'].endswith('.zip') and not r.content.startswith(b'PK'):
                raise ValueError('Expected ZIP; received non-ZIP response')
            if spec['file'].endswith('.pdf') and not r.content.startswith(b'%PDF'):
                raise ValueError('Expected PDF; received non-PDF response')
            path.write_bytes(r.content)
            meta.update(status='ok', resolved_url=r.url, bytes=len(r.content), sha256=hashlib.sha256(r.content).hexdigest())
            meta_path.write_text(json.dumps(meta, indent=2), encoding='utf-8')
            return meta
        except (requests.RequestException, ValueError) as error:
            meta.update(status='failed', error=str(error))
            if attempt < 2: time.sleep(1 + attempt)
    return meta

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--refresh', action='store_true')
    parser.add_argument('--source', choices=['ipeds','eada','nacda','documentation'])
    args = parser.parse_args()
    specs = json.loads((ROOT/'config/sources.json').read_text())
    active_files={x['file'] for x in specs}
    if args.source: specs = [x for x in specs if x['source']==args.source]
    with ThreadPoolExecutor(max_workers=4) as pool:
        results = list(pool.map(lambda s: fetch(s, args.refresh), specs))
    manifest = ROOT/'data/provenance/download_manifest.json'
    old = json.loads(manifest.read_text()) if manifest.exists() else []
    retired=[x for x in old if x['file'] not in active_files]
    if retired:
        (manifest.parent/'retired_url_probes.json').write_text(json.dumps(retired,indent=2),encoding='utf-8')
    by_file = {x['file']:x for x in old if x['file'] in active_files}
    by_file.update({x['file']:x for x in results})
    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps(sorted(by_file.values(), key=lambda x:x['file']), indent=2), encoding='utf-8')
    failed=[x for x in results if x['status']!='ok']
    print(f'Downloads: {len(results)-len(failed)} available; {len(failed)} failed')
    for item in failed: print(item['file'],item['error'])
    if failed: raise SystemExit(1)

if __name__=='__main__': main()
