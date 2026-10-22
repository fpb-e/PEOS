#!/usr/bin/env python3
from pathlib import Path
import argparse, json

BAD_TIME_PLACEHOLDERS={"UNAVAILABLE","N/A","UNKNOWN","NONE","NULL",""}

def main():
    ap=argparse.ArgumentParser(description="PEOS next-spec plain UTF-8 full-known-visible-source logger")
    ap.add_argument("events_jsonl"); ap.add_argument("output")
    a=ap.parse_args()
    events=[json.loads(x) for x in Path(a.events_jsonl).read_text(encoding="utf-8").splitlines() if x.strip()]
    out=["PEOS SESSION LOG",
         "SCHEMA: REV0_307_CANDIDATE / PLAIN_VERBATIM / SOURCE_GAP_TYPED",
         "TARGET_REVISION_LABEL: rev0.307",
         ""]
    counts={}
    for i,e in enumerate(events,1):
        if e["seq"]!=i: raise SystemExit(f"SEQ_NOT_CONTIGUOUS:{i}")
        et=e["event_type"]; counts[et]=counts.get(et,0)+1
        body=e.get("body_verbatim","")
        if et not in ("source_gap","attachment_event") and body=="": raise SystemExit(f"EMPTY_VERBATIM_BODY:{i}")
        tm=e["time"]
        out += [f"[SEQ {i:06d}]",
                f'TURN_ID: {e["turn_id"]}',
                f'EVENT_ORDER: {e["event_order"]}',
                f'ROLE: {e["role"]}',
                f'CHANNEL: {e["channel"]}',
                f'EVENT_TYPE: {et}',
                f'TURN_TIME_STATUS: {tm["TURN_TIME_STATUS"]}',
                f'TIME_EVIDENCE_CLASS: {tm["TIME_EVIDENCE_CLASS"]}',
                f'TIME_AUTHORITY: {tm["TIME_AUTHORITY"]}']
        ujst=tm.get("USER_TURN_OBSERVED_AT_JST")
        if ujst is not None:
            if str(ujst).strip().upper() in BAD_TIME_PLACEHOLDERS:
                raise SystemExit(f"USER_TURN_TIME_PLACEHOLDER_PROHIBITED:{i}")
            out.append(f"USER_TURN_OBSERVED_AT_JST: {ujst}")
        if et=="attachment_event":
            att=e.get("attachment") or {}
            for k in ("ATTACHMENT_REF","DISPLAY_NAME","BUNDLE_MEMBER_PATH","BYTES","SHA256","SNIFFED_MIME"):
                if k in att: out.append(f"{k}: {att[k]}")
        if et=="source_gap":
            out += ["RECOVERY_STATUS: VERBATIM_UNAVAILABLE",
                    f'SOURCE_GAP_REASON: {e.get("source_gap_reason","UNSPECIFIED")}',
                    "SUMMARY_NOT_USED_AS_TRANSCRIPT: TRUE"]
        out += ["BODY_VERBATIM_BEGIN", body, "BODY_VERBATIM_END", ""]
    out += ["[COUNTS]"] + [f"{k.upper()}: {v}" for k,v in sorted(counts.items())] + ["END_OF_LOG"]
    Path(a.output).write_text("\n".join(out)+"\n",encoding="utf-8")

if __name__=="__main__": main()
