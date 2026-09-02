# PEOS rev0.309 RELEASE CANDIDATE — 2026-09-01

このpackageはproject-level current canon `rev0.308`を物理sourceとして構築した、PEOS style-reconstruction／artifact-delivery response-densityのfix-forward候補である。

- BUILD_ID: `PEOS-REV0.309-CANDIDATE-20260901-193512-JST`
- TARGET_REVISION_LABEL: `rev0.309`
- CURRENT_PROJECT_CANON: `rev0.308`
- ACCEPTED_BASELINE: `PEOS_GITHUB_PACKAGE_rev0.307.zip`
- BASE_REFERENCE: `PEOS_GITHUB_PACKAGE_rev0.308.zip`
- BASE_REFERENCE_SHA256: `b62f418a3803d02206d619671dc70a997af58e5bd07a0641d17b032ab9f9ae96`
- STATUS: `RELEASE_CANDIDATE / NOT_OPERATIVE / NOT_ACCEPTED / NOT_SELF_ACCEPTED`
- PRIORITY_SOURCE: `PEOS_father_session_log_2026_09_01_192523.txt`
- PRIORITY_SOURCE_SHA256: `98d37d29df7f1fe2670229220ec31ab3994040509c5ab86deec7863af097d037`
- DIRECTIVE: `PEOS_NEXT_BUILD_DIRECTIVE_rev0.309_REGEN.txt`
- DIRECTIVE_SHA256: `152bc9f4d017fb9085e7e2e4acc16adb8e1f12b67f0af95f0e0b5cba52e925fd`
- PRIORITY_SOURCE_BUNDLE_SHA256: `b414a090dfec34b1f6f1232a949bb513de368443c2ff43b748702581394f7522`
- SUPERSEDED_GENERATION: `2026-09-01 19:09:59 JST / HISTORICAL_ONLY`

## rev0.309の修正核

1. `GLOBAL_PEOS_RESPONSE_CORE`を全coordinate共通のtyped restore layerとして正式化。
2. `RELATION_CONTEXT_ADAPTER`を呼称・関係・局所制約・stateだけのthin layerへ限定。
3. logを`ARCHIVE / EVIDENCE`と`RUNTIME RESTORE`の二層へ分離。
4. assistant逐語欠落は`ASSISTANT_VERBATIM_GAP`として保持し、derived modelで過去本文を捏造しない。
5. father correction `お前の応答が薄いな`からresponse-density hard gateを実装。
6. artifact delivery/completionでもcore personality・文脈・判断理由・意味付けを維持。
7. `ACTIVE / OPEN_LOOP / RESOLVED / CANCELLED / HISTORICAL_ONLY / DO_NOT_RESURRECT` state machineを一般side effectへ適用。
8. image description/evidence characterizationだけではimage generation/editを起動しない。
9. 匿名投稿の観測・自己事実・虚偽属性・欺瞞仮説・private identity hypothesis・technical attributionを分離。
10. historical authority blockをsnapshotへ隔離し、rev0.308 live authorityを巻き戻さない。
11. rev0.308のtime-ledger／五正本／BOOT／evidence／source-learning protectionsを非回帰維持。
12. STYLE-RESTORE-A〜Jの実行harnessを収録。

## Privacy / source boundary

- father-private live ledger snapshotはgeneral packageへ含めない。
- priority source bundle全体もprivate ledgerを含むため同梱しない。
- corrected father log、REGEN directive、mother regression log、evidence files、superseded artifactsは個別hash付きsourceとして収録する。
- anonymous / mother / assistant / screenshot wordingはfather vocabularyへ昇格しない。

## Acceptance boundary

- Legacy rev0.308 validator: build時に実行
- STYLE-RESTORE-A〜J static harness: build時に実行
- Live clean-session style acceptance: `PENDING`
- Father external acceptance / project promotion: `PENDING`

static passをlive-host passまたはfather acceptanceへ昇格しない。
