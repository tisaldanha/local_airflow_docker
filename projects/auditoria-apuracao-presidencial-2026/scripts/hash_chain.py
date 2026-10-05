#!/usr/bin/env python3
import argparse, csv, hashlib, json
from pathlib import Path

def sha256(b):
    return hashlib.sha256(b).hexdigest()

def canonical_json_hash(raw):
    try:
        obj=json.loads(raw.decode("utf-8"))
    except Exception:
        return ""
    canonical=json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False).encode("utf-8")
    return sha256(canonical)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",required=True)
    ap.add_argument("--out",default="output/hash_manifest.csv")
    args=ap.parse_args()

    root=Path(args.input)
    files=sorted(p for p in root.rglob("*") if p.is_file())
    prev_chain="0"*64
    rows=[]

    for p in files:
        raw=p.read_bytes()
        raw_hash=sha256(raw)
        canon=canonical_json_hash(raw)
        chain=sha256((prev_chain+raw_hash+str(p.relative_to(root))).encode())
        rows.append({
            "path":str(p.relative_to(root)),
            "bytes":len(raw),
            "raw_sha256":raw_hash,
            "canonical_json_sha256":canon,
            "chain_sha256":chain,
        })
        prev_chain=chain

    out=Path(args.out)
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",newline="",encoding="utf-8") as f:
        fields=["path","bytes","raw_sha256","canonical_json_sha256","chain_sha256"]
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    print(f"hashed={len(rows)} final_chain={prev_chain}")

if __name__=="__main__":
    main()
