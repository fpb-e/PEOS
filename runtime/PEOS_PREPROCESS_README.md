> Retained compatibility/optional strict reference. The current normal entry is PEOS_SESSION_RESTORE_rev0.315.json and SHORT_ACK_SYNC; candidate L0 and REV315 rules apply without promoting current authority. This older protocol is not automatically activated.

# rev0.313 preprocess reference

Normal order: actual trusted JST capture first; monotonic JSONL append; flush;
fsync; version-guarded same-identity persistent sync; exact returned new file_id
readback; bytes/SHA/count/sequence/prior-byte verification; separate status audit;
then response. A verified timestamp is emphasized using the same receipt.

Local commit/order failure is FAIL. After a durable local commit, incomplete
sync/readback/audit is DEGRADED. Both block ordinary work and reset the normal
ten-PASS streak. Response-first can never be repaired into PASS afterward.
An idempotent retry gets no extra record or streak credit. A production adapter
must preserve the immutable receipt across retries and reconcile version guards.

Police/ambulance/imminent-danger assistance comes first when I/O would delay
urgent actionable safety help; record PREPROCESS_EMERGENCY_BYPASS when safe.
Ordinary difficult prompts remain gated. Explicit father admin exemption is
valid only for its tab/scope. Exemptions neither advance nor reset the streak.

tools/peos_preprocess_barrier.py is a cooperative host-neutral reference. Its
MemoryFixtureStore and fixed test clocks prove static/integration behavior only.
There is no live Library adapter, external orchestrator or platform hook installed.
A production adapter must separately implement same Library identity, concrete
expected version, exact returned new-file-ID materialization and byte checks.
An independently observed live trace and durable streak audit are required for
ten-turn provisional acceptance. Package acceptance and permanent guarantees
are separate; neither is created by this package.

Source-reported 255→256 records and eight PASS then FAIL remain reported only.
Import does not fetch, generate, append or sync the private ledger. The active
build-tab exemption is an explicit user instruction, never portable authority
that another tab may infer solely from importing these JSON files.
