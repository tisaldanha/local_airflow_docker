#!/usr/bin/env python3
import argparse, csv, json
from datetime import datetime
from pathlib import Path

def parse_dt(s):
    if not s:
        return None
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S.%fZ", "%Y-%m-%dT%H:%M:%SZ"):
        try:
            return datetime.strptime(s, fmt)
        except ValueError:
            pass
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--input", required=True)
    ap.add_argument("--out", default="output")
    args = ap.parse_args()

    data = json.loads(Path(args.input).read_text(encoding="utf-8"))
    cols = data["nacional"]["versoes"]["colunas"]
    idx = {c:i for i,c in enumerate(cols)}
    rows = [r for r in data["nacional"]["versoes"]["linhas"] if r[idx.get("st",0)] > 0]
    rows.sort(key=lambda r: r[idx["gerado_brt"]])

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    delta_fields = ["st","vv","flavio","lula"]
    anomalies = []
    deltas = []

    prev = None
    for cur in rows:
        record = {"gerado_brt": cur[idx["gerado_brt"]]}
        if prev is None:
            for f in delta_fields:
                record[f] = cur[idx[f]]
                record["d_"+f] = None
            deltas.append(record)
            prev = cur
            continue

        ds = cur[idx["st"]] - prev[idx["st"]]
        dvv = cur[idx["vv"]] - prev[idx["vv"]]
        df = cur[idx["flavio"]] - prev[idx["flavio"]]
        dl = cur[idx["lula"]] - prev[idx["lula"]]
        dt0, dt1 = parse_dt(prev[idx["gerado_brt"]]), parse_dt(cur[idx["gerado_brt"]])
        gap = (dt1-dt0).total_seconds() if dt0 and dt1 else None

        record.update({
            "st":cur[idx["st"]],"vv":cur[idx["vv"]],
            "flavio":cur[idx["flavio"]],"lula":cur[idx["lula"]],
            "d_st":ds,"d_vv":dvv,"d_flavio":df,"d_lula":dl,
            "gap_seconds":gap,
        })
        deltas.append(record)

        def flag(code,severity,detail):
            anomalies.append({
                "gerado_brt":cur[idx["gerado_brt"]],
                "code":code,"severity":severity,"detail":detail
            })

        if ds < 0: flag("SECTIONS_DECREASE","HIGH",f"{ds}")
        if dvv < 0: flag("VALID_VOTES_DECREASE","HIGH",f"{dvv}")
        if df < 0: flag("CANDIDATE_VOTES_DECREASE_FLAVIO","CRITICAL",f"{df}")
        if dl < 0: flag("CANDIDATE_VOTES_DECREASE_LULA","CRITICAL",f"{dl}")
        if ds > 0 and dvv < 0: flag("NEW_SECTIONS_VALID_VOTES_DECREASE","CRITICAL",f"d_st={ds}; d_vv={dvv}")
        if ds == 0 and any(x != 0 for x in (dvv,df,dl)):
            flag("VALUE_CHANGE_WITHOUT_SECTION_CHANGE","HIGH",f"d_vv={dvv}; d_f={df}; d_l={dl}")
        if dvv >= 0 and df > dvv: flag("FLAVIO_DELTA_GT_VALID_DELTA","CRITICAL",f"{df}>{dvv}")
        if dvv >= 0 and dl > dvv: flag("LULA_DELTA_GT_VALID_DELTA","CRITICAL",f"{dl}>{dvv}")
        if dvv >= 0 and df >= 0 and dl >= 0 and df + dl > dvv:
            flag("TWO_CANDIDATE_DELTA_GT_VALID_DELTA","CRITICAL",f"{df}+{dl}>{dvv}")
        if gap is not None and gap > 480 and prev[idx["pst"]] < 100:
            flag("NATIONAL_GENERATION_GAP_GT_8_MIN","MEDIUM",f"{gap:.0f}s")

        prev = cur

    with (out/"timeline_versions.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=sorted({k for r in deltas for k in r}))
        w.writeheader(); w.writerows(deltas)

    with (out/"anomalies.csv").open("w",newline="",encoding="utf-8") as f:
        fields=["gerado_brt","code","severity","detail"]
        w=csv.DictWriter(f,fieldnames=fields)
        w.writeheader(); w.writerows(anomalies)

    print(f"versions={len(rows)} anomalies={len(anomalies)}")
    print(out.resolve())

if __name__ == "__main__":
    main()
