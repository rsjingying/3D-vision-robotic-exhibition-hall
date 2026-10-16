"""Restore pinned source assets using the checked-in provenance manifest."""
from pathlib import Path
import concurrent.futures,hashlib,json,urllib.request
ROOT=Path(__file__).resolve().parent/'source'
manifest=json.loads((ROOT/'provenance.json').read_text())
def restore(item):
 path=ROOT/item['brand']/item['path']
 if path.exists() and hashlib.sha256(path.read_bytes()).hexdigest()==item['sha256']:return
 request=urllib.request.Request(item['url'],headers={'User-Agent':'VISION-FLOW'})
 with urllib.request.urlopen(request,timeout=90) as response:data=response.read()
 if hashlib.sha256(data).hexdigest()!=item['sha256']:raise ValueError('Source hash mismatch: '+item['path'])
 path.parent.mkdir(parents=True,exist_ok=True);path.write_bytes(data)
with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:list(pool.map(restore,manifest))
print('Verified',len(manifest),'pinned source files')
