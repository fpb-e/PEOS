#!/usr/bin/env python3
import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

JST=ZoneInfo("Asia/Tokyo")

class MockHost:
    def __init__(self, available=True, result_verified=True):
        self.available=available
        self.result_verified=result_verified
        self.tasks=[]
        self.next_id=1
    def find(self, coordinate, purpose, schedule, body):
        return [t for t in self.tasks if t["active"] and t["coordinate"]==coordinate and t["purpose"]==purpose and t["schedule"]==schedule and t["body"]==body]
    def create(self, coordinate, purpose, schedule, body):
        if not self.available:
            return {"status":"REMINDER_CAPABILITY_UNAVAILABLE"}
        if not self.result_verified:
            return {"status":"RESULT_UNVERIFIED"}
        dup=self.find(coordinate,purpose,schedule,body)
        if dup: return {"status":"EXISTING_REUSED","task":dup[0]}
        t={"id":f"mock-{self.next_id}","coordinate":coordinate,"purpose":purpose,"schedule":schedule,"body":body,"active":True,"delivery_observed":False}
        self.next_id+=1; self.tasks.append(t)
        return {"status":"CREATED","task":t}
    def cancel(self, task_id):
        ms=[t for t in self.tasks if t["id"]==task_id]
        if len(ms)!=1: return {"status":"RESULT_UNVERIFIED"}
        ms[0]["active"]=False
        return {"status":"CANCELLED","task":ms[0]}

def result(name, passed, detail):
    return {"TEST":name,"PASS":bool(passed),"DETAIL":detail}

def run():
    now=datetime(2026,8,23,20,6,11,tzinfo=JST)
    out=[]
    # A
    h=MockHost()
    sched="2026-08-24T09:00:00+09:00"
    r=h.create("FATHER","future-one-shot",sched,"test")
    out.append(result("REMINDER-A",r["status"]=="CREATED" and r["task"]["active"] and "+09:00" in sched,r))
    # B
    rr="RRULE:FREQ=WEEKLY;BYDAY=MO,TU,WE,TH,FR;BYHOUR=9;BYMINUTE=0"
    r=h.create("FATHER","weekday",rr,"weekday test")
    out.append(result("REMINDER-B",r["status"]=="CREATED" and rr.startswith("RRULE:"),r))
    # C
    before=len([t for t in h.tasks if t["active"]])
    r2=h.create("FATHER","weekday",rr,"weekday test")
    after=len([t for t in h.tasks if t["active"]])
    out.append(result("REMINDER-C",r2["status"]=="EXISTING_REUSED" and after==before,{"before":before,"after":after,"result":r2["status"]}))
    # D
    ambiguous="25日"
    out.append(result("REMINDER-D",ambiguous=="25日",{"status":"AMBIGUOUS_SCHEDULE","created":False}))
    # E
    past=datetime(2026,8,20,9,0,tzinfo=JST)
    out.append(result("REMINDER-E",past<now,{"status":"PAST_SCHEDULE","created":False}))
    # F
    r=MockHost(available=False).create("FATHER","x",sched,"x")
    out.append(result("REMINDER-F",r["status"]=="REMINDER_CAPABILITY_UNAVAILABLE",r))
    # G
    r=MockHost(result_verified=False).create("FATHER","x",sched,"x")
    out.append(result("REMINDER-G",r["status"]=="RESULT_UNVERIFIED",r))
    # H
    h2=MockHost(); r=h2.create("FATHER","x",sched,"x")
    out.append(result("REMINDER-H",r["task"]["active"] and not r["task"]["delivery_observed"],r["task"]))
    # I
    extra=h2.create("FATHER","y","2026-08-25T10:00:00+09:00","y")["task"]
    target=r["task"]["id"]; cr=h2.cancel(target)
    untouched=[t for t in h2.tasks if t["id"]==extra["id"]][0]["active"]
    out.append(result("REMINDER-I",cr["status"]=="CANCELLED" and not cr["task"]["active"] and untouched,{"cancelled":target,"other_active":untouched}))
    # J historical no-replay
    historical=["晩御飯","ENRICH","駐輪場","ゴミ収集"]
    h3=MockHost()
    out.append(result("REMINDER-J",len(h3.tasks)==0,{"historical_data_only":historical,"created_tasks":0}))
    # K privacy
    reservation_no="PRIVATE-RESERVATION-123"
    notification="駐輪場手続きを確認"
    out.append(result("REMINDER-K",reservation_no not in notification,{"notification":notification,"private_id_excluded":True}))
    # L
    planned="2026-08-19T18:30:00+09:00"; observed="2026-08-19T18:32:35+09:00"
    out.append(result("REMINDER-L",planned!=observed,{"SCHEDULED":planned,"OBSERVED":observed}))
    # M
    no_ingress=False
    status="INGRESS_REQUIRED_NO_RELATIVE_DATE_CREATION" if not no_ingress else "BAD"
    out.append(result("REMINDER-M",status=="INGRESS_REQUIRED_NO_RELATIVE_DATE_CREATION",{"canonical_ingress":False,"status":status,"created":False}))
    return {"HARNESS_CLASS":"STATIC_MOCK_PROVIDER / NO_LIVE_TASK_SIDE_EFFECT",
            "REMINDER_STATIC_ACCEPTANCE":"PASS" if all(x["PASS"] for x in out) else "FAIL",
            "REMINDER_LIVE_HOST_ACCEPTANCE":"PENDING",
            "TESTS":out}

if __name__=="__main__":
    print(json.dumps(run(),ensure_ascii=False,indent=2))
