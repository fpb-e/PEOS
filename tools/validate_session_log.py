#!/usr/bin/env python3
from pathlib import Path
import argparse,re,json,sys

PLACEHOLDER_RE=re.compile(r"^USER_TURN_OBSERVED_AT_JST:\s*(?:UNAVAILABLE|N/?A|UNKNOWN|NONE|NULL)?\s*$",re.M|re.I)
PER_BODY_FORBIDDEN=[
    re.compile(r"^BODY_UTF8_BYTES:",re.M),
    re.compile(r"^BODY_SHA256:",re.M),
    re.compile(r"^BODY_BEGIN_[0-9a-fA-F]{8,}",re.M),
    re.compile(r"^BODY_END_[0-9a-fA-F]{8,}",re.M),
]

def inspect(path):
    t=Path(path).read_text(encoding="utf-8",errors="replace")
    reasons=[]
    seqs=[int(x) for x in re.findall(r"^\[SEQ\s+(\d+)\]",t,re.M)]
    if not seqs or seqs!=list(range(1,len(seqs)+1)): reasons.append("SEQ_NOT_CONTIGUOUS")
    if not re.search(r"^(?:END_OF_LOG|END_OF_PEOS_FATHER_SESSION_LOG)$", t, re.M):
        reasons.append("END_OF_LOG_MISSING")
    if PLACEHOLDER_RE.search(t): reasons.append("HISTORICAL_USER_TURN_TIME_PLACEHOLDER")
    for rx in PER_BODY_FORBIDDEN:
        if rx.search(t): reasons.append("PER_BODY_HASH_METADATA_OR_HASH_BOUNDARY")
    bb=len(re.findall(r"^BODY_VERBATIM_BEGIN$",t,re.M)); be=len(re.findall(r"^BODY_VERBATIM_END$",t,re.M))
    if bb!=be or bb==0: reasons.append("PLAIN_BODY_BOUNDARY_MISMATCH")
    summaries=len(re.findall(r"ASSISTANT_RESPONSE_SUMMARY",t))
    assistant_events=len(re.findall(r"EVENT_TYPE: assistant_(?:commentary|final)",t))
    if summaries and assistant_events==0: reasons.append("SUMMARY_ONLY_ASSISTANT_CONTENT")
    if "FULL_KNOWN_VISIBLE_SOURCE_LOG" in t and summaries and assistant_events==0: reasons.append("OVERCLAIMED_FULL_REINJECTABLE_STATUS")
    return {"path":str(path),"seq_count":len(seqs),"body_block_count":bb,
            "assistant_verbatim_events":assistant_events,"summary_markers":summaries,
            "per_body_hash_metadata_count":sum(len(rx.findall(t)) for rx in PER_BODY_FORBIDDEN),
            "historical_user_turn_jst_placeholder_count":len(PLACEHOLDER_RE.findall(t)),
            "reasons":sorted(set(reasons)),"pass":not reasons}

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("log"); ap.add_argument("--expect-negative",action="store_true"); ap.add_argument("--json-out")
    a=ap.parse_args(); r=inspect(a.log)
    ok=(not r["pass"]) if a.expect_negative else r["pass"]
    r["expect_negative"]=a.expect_negative; r["expectation_met"]=ok
    s=json.dumps(r,ensure_ascii=False,indent=2)
    if a.json_out: Path(a.json_out).write_text(s+"\n",encoding="utf-8")
    print(s)
    if not ok: sys.exit(1)
if __name__=="__main__": main()
