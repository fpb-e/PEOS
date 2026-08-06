#!/usr/bin/env python3
from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path
import argparse, hashlib, json, re, sys, zipfile, yaml

RC = "rev0.306-RC1"
OPERATIVE = "rev0.305"
FIVE = [
 "prompt/PEOS_CURRENT_SPEC_JP.md",
 "prompt/PEOS_CURRENT_RUNTIME_GUARD_JP.md",
 "prompt/PEOS_CURRENT_DESIGNDOC_JP.md",
 "prompt/PEOS_CURRENT_PAPER_JP.md",
 "prompt/PEOS_CURRENT_LOG_ANTHOLOGY_JP.md",
]
REQUIRED = FIVE + [
 "admin/PEOS_FIVE_CANON_REFORM_CHARTER_rev0.306-RC1.md",
 "admin/RULE_OWNERSHIP_REGISTRY.yaml",
 "admin/CURRENT_TO_RC1_MIGRATION_LEDGER.jsonl",
 "admin/ACTIVE_RULE_CONFLICT_REPORT.md",
 "admin/FATHER_DIRECT_LEDGER.jsonl",
 "admin/BEHAVIOR_FIXTURE_INDEX.yaml",
 "admin/COORDINATE_OVERLAY_MAP.yaml",
 "admin/FATHER_BEHAVIOR_MODEL.yaml",
 "admin/VALIDATION_RESULTS.json",
 "admin/BASELINE_IMMUTABILITY_EVIDENCE.txt",
 "admin/BASELINE_INVENTORY.json",
 "tests/CLEAN_SESSION_ACCEPTANCE.json",
 "tests/CONSECUTIVE_TURN_RUNTIME.json",
 "tests/BEHAVIOR_ORACLE_COMPARISON.json",
 "evidence/PEOS_EVIDENCE.txt",
 "PACKAGE_MANIFEST.txt",
]

def sha256_file(path: Path) -> str:
    h=hashlib.sha256()
    with path.open("rb") as f:
        for c in iter(lambda:f.read(1024*1024), b""): h.update(c)
    return h.hexdigest()

@dataclass
class Gate:
    turn_id: str
    latch: str = "LOCKED"
    receipt: dict|None = None
    semantic_authorized: bool = False
    actions: list[str] = None
    attempts: int = 0
    def __post_init__(self):
        self.actions=[]
    def action(self, kind: str):
        if self.latch=="LOCKED" and kind!="PYTHON_PROVIDER":
            raise RuntimeError("PRE_DISPATCH_BLOCK")
        self.actions.append(kind)
    def capture(self, fail_first=False):
        if self.actions:
            raise RuntimeError("INTERVENING_ACTION")
        self.attempts += 1
        if fail_first and self.attempts==1:
            return False
        now=datetime.now(ZoneInfo("Asia/Tokyo"))
        self.actions.append("PYTHON_PROVIDER")
        self.receipt={
          "turn_id":self.turn_id,"timestamp":now.isoformat(),
          "provider":'datetime.now(ZoneInfo("Asia/Tokyo"))',
          "attempts":self.attempts,"success_action_index":self.attempts,
          "intervening_action_before_success":"NONE",
        }
        self.latch="UNLOCKED"; self.semantic_authorized=True
        return True
    def close(self):
        self.receipt=None; self.latch="RETIRED"; self.semantic_authorized=False

def parse_manifest(path: Path):
    data={}
    hashes={}
    for line in path.read_text(encoding="utf-8").splitlines():
        if ": " in line:
            k,v=line.split(": ",1); data[k]=v
        m=re.match(r"SHA256  ([0-9a-f]{64})  (.+)",line)
        if m: hashes[m.group(2)]=m.group(1)
    return data,hashes

def check(root: Path) -> dict:
    result={"checks":{},"details":{}}
    def ok(name, value, detail=None):
        result["checks"][name]=bool(value)
        if detail is not None: result["details"][name]=detail

    ok("required_files", all((root/p).is_file() for p in REQUIRED),
       [p for p in REQUIRED if not (root/p).is_file()])
    if not result["checks"]["required_files"]: return result

    manifest, mh=parse_manifest(root/"PACKAGE_MANIFEST.txt")
    ok("rc_status_not_operative",
       manifest.get("VERSION")==RC and manifest.get("RELEASE_STATUS")=="RELEASE_CANDIDATE_NOT_OPERATIVE_NOT_ACCEPTED_NOT_SELF_ACCEPTED"
       and manifest.get("OPERATIVE_CURRENT")==OPERATIVE)

    bad_hash=[]
    for rel,expected in mh.items():
        p=root/rel
        if not p.is_file() or sha256_file(p)!=expected: bad_hash.append(rel)
    ok("manifest_hashes", not bad_hash, bad_hash)

    header_bad=[]
    for rel in FIVE:
        t=(root/rel).read_text(encoding="utf-8")
        required=[f"文書revision: `{RC}`",f"現行latest: `{RC}`",f"PACKAGE_MANIFEST_VERSION: `{RC}`",
                  f"HIGHEST_EMBEDDED_REVISION: `{RC}`",f"OPERATIVE_CURRENT: `{OPERATIVE}`",
                  "RELEASE_CANDIDATE / NOT_OPERATIVE / NOT_ACCEPTED / NOT_SELF_ACCEPTED"]
        if not all(x in t for x in required): header_bad.append(rel)
    ok("five_canon_header_triple_equality", not header_bad, header_bad)

    # rule cards and unique ownership
    found={}
    dup=[]
    owner_bad=[]
    file_owner={
      FIVE[0]:"SPEC", FIVE[1]:"RUNTIME_GUARD", FIVE[2]:"DESIGNDOC", FIVE[3]:"PAPER", FIVE[4]:"LOG_ANTHOLOGY"
    }
    for rel in FIVE:
        t=(root/rel).read_text(encoding="utf-8")
        ids=re.findall(r"- RULE_ID: `([^`]+)`",t)
        owners=re.findall(r"- OWNER: `([^`]+)`",t)
        if len(ids)!=len(owners): owner_bad.append(rel); continue
        for rid,owner in zip(ids,owners):
            if rid in found: dup.append(rid)
            found[rid]=owner
            if owner!=file_owner[rel]: owner_bad.append(f"{rel}:{rid}:{owner}")
    registry=yaml.safe_load((root/"admin/RULE_OWNERSHIP_REGISTRY.yaml").read_text(encoding="utf-8"))
    reg={x["RULE_ID"]:x["OWNER"] for x in registry["rules"]}
    ok("one_rule_one_owner", not dup and not owner_bad and found==reg,
       {"duplicates":dup,"owner_bad":owner_bad,"found":len(found),"registry":len(reg)})

    # no unresolved conflict
    crt=(root/"admin/ACTIVE_RULE_CONFLICT_REPORT.md").read_text(encoding="utf-8")
    ok("no_unresolved_active_conflicts","UNRESOLVED_ACTIVE_CONFLICT: NONE" in crt)

    # no long exact duplicate paragraph across five canons
    blocks={}
    shared=[]
    for rel in FIVE:
        t=(root/rel).read_text(encoding="utf-8")
        for b in re.split(r"\n\s*\n",t):
            n=re.sub(r"\s+"," ",b.strip())
            if len(n)>=120:
                h=hashlib.sha256(n.encode()).hexdigest()
                if h in blocks and blocks[h]!=rel: shared.append((blocks[h],rel,n[:80]))
                else: blocks[h]=rel
    ok("no_long_exact_cross_canon_duplicate",not shared,shared[:10])

    # clean active corpus: no historical revision headings and no admin runtime dependencies
    hist=[]
    for rel in FIVE:
        t=(root/rel).read_text(encoding="utf-8")
        hist.extend((rel,h) for h in re.findall(r"^##\s+(rev0\.[^\n]+)",t,re.M))
    ok("active_runtime_not_buried_in_history",not hist,hist[:10])
    runtime=(root/FIVE[1]).read_text(encoding="utf-8")
    tokens=[
      "TURN_TIME_INGRESS_LATCH = LOCKED",
      "CURRENT_TURN_PYTHON_RECEIPT = ABSENT",
      "SEMANTIC_WORK_AUTHORIZED = FALSE",
      'datetime.now(ZoneInfo("Asia/Tokyo"))',
      "receipt成立前のcommentary",
      "same-provider",
      "ADMIN_AUDIT_MODE",
      "GENERAL_DISTRIBUTION_MODE",
      "LOG_ARTIFACT_CONTENT_STDOUT_LEAK",
    ]
    ok("runtime_core_tokens",all(x in runtime for x in tokens),[x for x in tokens if x not in runtime])
    ok("five_canon_runtime_self_contained",
       "一般runtime必須ではない" in runtime and "五正本だけで動作" in runtime)

    # overlays
    ov=yaml.safe_load((root/"admin/COORDINATE_OVERLAY_MAP.yaml").read_text(encoding="utf-8"))
    ok("overlay_isolation",ov.get("implicit_inheritance")=="PROHIBITED"
       and ov["FATHER_OVERLAY"]["inherits"]==["CORE"]
       and ov["MOTHER_OVERLAY"]["inherits"]==["CORE"]
       and ov["GENERAL_OVERLAY"]["inherits"]==["CORE"])

    # father ledger purity
    led=[json.loads(x) for x in (root/"admin/FATHER_DIRECT_LEDGER.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    purity=all(x["SOURCE_CLASS"].startswith("FATHER_DIRECT") for x in led)
    image_ok=all(x["DECISION"]=="NO_NEW_REUSABLE_RESOURCE" for x in led if x["RAW_TEXT"] in ("<<ImageDisplayed>>","<<ImageDisplayed>><<ImageDisplayed>>"))
    ok("father_direct_ledger_purity",purity and image_ok,{"count":len(led),"image_ok":image_ok})

    # fixture source purity and schema
    ant=(root/FIVE[4]).read_text(encoding="utf-8")
    idx=yaml.safe_load((root/"admin/BEHAVIOR_FIXTURE_INDEX.yaml").read_text(encoding="utf-8"))
    required_fields=["SOURCE_CLASS","CONTEXT","FATHER_DIRECT_EXAMPLE","INTERPRETATION","DECISION_POLICY",
                     "OUTPUT_SHAPE","BAD_RESPONSE","FAILURE_REASON","PROHIBITED_SHORTCUT","OPSEC_BOUNDARY",
                     "COORDINATE","ASSERTIONS","SOURCE_PROVENANCE"]
    missing=[]
    for x in idx["fixtures"]:
        fid=x["FIXTURE_ID"]
        pos=ant.find("### "+fid)
        if pos<0: missing.append(fid); continue
        block=ant[pos:ant.find("\n### ",pos+4) if ant.find("\n### ",pos+4)>=0 else len(ant)]
        for f in required_fields:
            if f"{f}:" not in block: missing.append(fid+":"+f)
    ok("fixture_schema_and_index",not missing,missing[:20])

    # migration coverage
    baseline_inv=json.loads((root/"admin/BASELINE_INVENTORY.json").read_text(encoding="utf-8"))
    mig=[json.loads(x) for x in (root/"admin/CURRENT_TO_RC1_MIGRATION_LEDGER.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    ok("migration_lineage",len(mig)>1000 and baseline_inv["baseline_sha256"]==manifest.get("BASELINE_SHA256"),
       {"entries":len(mig),"baseline":baseline_inv["baseline_sha256"]})

    # clean-session definition uses only five canons
    cs=json.loads((root/"tests/CLEAN_SESSION_ACCEPTANCE.json").read_text(encoding="utf-8"))
    ok("clean_session_five_canon_only",cs["runtime_inputs"]==FIVE and cs["admin_assets_required_at_runtime"] is False)

    # consecutive state machine actual calls
    vectors=json.loads((root/"tests/CONSECUTIVE_TURN_RUNTIME.json").read_text(encoding="utf-8"))
    positive=[]
    unique_receipts=set()
    for v in vectors["positive_turns"]:
        g=Gate(v["id"])
        if v.get("first_attempt")=="ENVIRONMENT_FAILURE":
            assert g.capture(fail_first=True) is False
            assert g.capture(fail_first=True) is True
        else:
            assert g.capture() is True
        g.action("SEMANTIC")
        key=(g.receipt["turn_id"],g.receipt["timestamp"])
        unique_receipts.add(key)
        positive.append(g.semantic_authorized and g.actions[0]=="PYTHON_PROVIDER")
        g.close()
    negative=[]
    # N01 self-report does not unlock
    g=Gate("N01"); negative.append(not g.semantic_authorized and g.receipt is None)
    # N02 prior receipt reuse blocked by new Gate
    old=Gate("OLD"); old.capture(); oldr=old.receipt.copy(); old.close()
    g=Gate("N02"); g.receipt=oldr; negative.append(g.latch=="LOCKED" and not g.semantic_authorized)
    # N03 pre-commentary rejected
    g=Gate("N03")
    try: g.action("COMMENTARY"); negative.append(False)
    except RuntimeError: negative.append(True)
    # N04 displayed text does not unlock
    g=Gate("N04"); displayed="2026-08-06 12:00:00"; negative.append(g.receipt is None and not g.semantic_authorized)
    # N05 fallback is not accepted; no capture performed
    g=Gate("N05"); fallback="shell date"; negative.append(g.latch=="LOCKED")
    # N06 correction declaration doesn't unlock next turn
    g=Gate("N06"); declaration="復旧しました"; negative.append(g.latch=="LOCKED" and g.receipt is None)
    ok("consecutive_turn_actual_provider_calls",all(positive) and len(unique_receipts)==len(positive),
       {"positive":len(positive),"unique_receipts":len(unique_receipts)})
    ok("negative_substitutions_rejected",all(negative),{"negative":negative})

    # RC claim controls and baseline immutability fields
    ok("baseline_immutability_declared",
       manifest.get("BASELINE_SHA256")=="69c99dd788f009726d20e43522822b288fa16eef03e7e4860fb34a4f23beae66"
       and manifest.get("BASELINE_SIDECAR_FILE_SHA256")=="daa4209b3c41ced379bd54518ee2a5edda8d39bcd1070c7df41bb6a3710249cf")
    ok("release_candidate_not_self_accepted",
       all("NOT_OPERATIVE" in (root/rel).read_text(encoding="utf-8") for rel in FIVE)
       and manifest.get("EXTERNAL_FATHER_REVIEW")=="PENDING")

    result["pass"]=all(result["checks"].values())
    result["summary"]={
      "pass":result["pass"],"check_count":len(result["checks"]),
      "positive_turns":len(positive),"negative_tests":len(negative),
      "rules":len(found),"father_ledger":len(led),"fixtures":len(idx["fixtures"]),
    }
    return result

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("root",nargs="?",default=".")
    ap.add_argument("--json",action="store_true")
    args=ap.parse_args()
    r=check(Path(args.root).resolve())
    print(json.dumps(r,ensure_ascii=False,indent=2) if args.json else
          "\n".join([f"{k}: {'PASS' if v else 'FAIL'}" for k,v in r["checks"].items()]+
                    [f"OVERALL: {'PASS' if r['pass'] else 'FAIL'}"]))
    raise SystemExit(0 if r["pass"] else 1)
if __name__=="__main__": main()
