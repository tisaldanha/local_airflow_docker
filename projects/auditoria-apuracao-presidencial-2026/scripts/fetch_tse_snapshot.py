#!/usr/bin/env python3
import argparse, hashlib, json, time
from datetime import datetime, timezone
from pathlib import Path
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--urls",required=True,help="arquivo com uma URL por linha")
    ap.add_argument("--out",default="data/raw")
    args=ap.parse_args()

    out=Path(args.out)
    out.mkdir(parents=True,exist_ok=True)
    urls=[x.strip() for x in Path(args.urls).read_text(encoding="utf-8").splitlines()
          if x.strip() and not x.strip().startswith("#")]

    for n,url in enumerate(urls,1):
        captured=datetime.now(timezone.utc)
        req=Request(url,headers={"User-Agent":"ElectionDataIntegrityAudit/1.0"})
        meta={"url":url,"captured_at_utc":captured.isoformat()}
        try:
            with urlopen(req,timeout=30) as r:
                body=r.read()
                meta.update({
                    "http_status":r.status,
                    "headers":dict(r.headers.items()),
                    "bytes":len(body),
                    "sha256":hashlib.sha256(body).hexdigest(),
                })
        except HTTPError as e:
            body=e.read()
            meta.update({"http_status":e.code,"headers":dict(e.headers.items()),"bytes":len(body),"sha256":hashlib.sha256(body).hexdigest(),"error":str(e)})
        except URLError as e:
            body=b""
            meta.update({"http_status":None,"headers":{},"bytes":0,"sha256":None,"error":str(e)})

        stamp=captured.strftime("%Y%m%dT%H%M%S.%fZ")
        stem=f"{stamp}_{n:04d}"
        (out/f"{stem}.bin").write_bytes(body)
        (out/f"{stem}.json").write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding="utf-8")
        print(stem, meta.get("http_status"), meta.get("bytes"), meta.get("sha256"))

if __name__=="__main__":
    main()
