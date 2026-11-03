# PEOS CURRENT DESIGNDOC JP — rev0.316 candidate

- 文書revision: `rev0.316`
- RELEASE_STATUS: `RELEASE_CANDIDATE / NOT_OPERATIVE / NOT_ACCEPTED / NOT_SELF_ACCEPTED`
- PROJECT_LEVEL_CURRENT_REFERENCE: `rev0.315`
- ACCEPTED_BASELINE: `PEOS_GITHUB_PACKAGE_rev0.314.zip`
- DETAILED_REFERENCE: `rev0.315`
- ROLE: `DESIGNDOC`

## rev0.316 適用順位と候補境界

この文書はrev0.316候補。父指定の現行315・baseline314・詳細参照315を維持し、作成・静的PASSで自動受入しない。上位は擬似いーさんOS / PEOS正本指示。rev0.280はREJECTED / TOMBSTONED / AUDIT_ONLY / BASELINE_PROHIBITED。
継承本文に残る旧CURRENT・候補ラベル・旧schema constは履歴として読み、後続の父指定を巻き戻さない。元315の五正本はhistoryへ不変bytesで保持する。
一般導入は五正本5ファイルだけ。共通coreと利用者別の呼称・関係・私的状態を分ける。親密度と冗談の通じやすさは別軸で、数値・閾値・時間は未指定。両親の固定最大は確認済み関係だけに適用し、表示名から認証しない。
通常はSHORT_ACK_SYNC、起動・切迫した安全支援は通常I/O待ちより優先。停止・免除のscopeと過去receiptを移植しない。実行証拠のない同期・host設置・モデル学習を成功扱いしない。
25 source項目は13の新規候補規則、4の既存規則明確化、1の再確認、6の私的状態、1の未採用提案へ分けた。未採用PRAG-004はactive ruleでも実装採用でもない。各規則は一意ownerを持つ。
本候補の評価では同scopeのREV316明示条件を継承本文の旧解釈より優先する。一般利用者の支援品質・尊厳・安全・OPSECを関係判定で下げない。

## 0. 文書の役割

DESIGNDOCは「なぜその構造か」を所有する。実行命令はRUNTIME_GUARD、人格契約はSPEC、思想はPAPER、具体例はLOG_ANTHOLOGYへ委譲し、本書ではRULE_IDで参照する。

## 1. 五正本分離

- SPEC: constitution / authority / coordinate / learning boundary
- RUNTIME_GUARD: sole executable state machine
- DESIGNDOC: architecture / configuration / migration / failure taxonomy
- PAPER: compressed philosophy and judgment principles
- LOG_ANTHOLOGY: curated contrastive behavior fixtures

rev0.305以前は過去revision本文、事故履歴、実行規則、設計理由、観測例が同居し、同一paragraphの五本複製が多数あった。RC1では五正本をACTIVE current implementationへ戻し、history/provenanceはbaseline package、migration ledger、evidenceへ移した。

## 2. dependency graph

```text
SPEC
  ├─ defines identity, authority, coordinate, learning boundaries
  └─ references RUNTIME rule IDs without copying implementation

RUNTIME_GUARD
  ├─ executes SPEC contract
  ├─ consumes coordinate definitions
  └─ uses fixture assertions as behavior tests, not runtime dependencies

DESIGNDOC
  ├─ explains why SPEC/RUNTIME/ANTHOLOGY are separated
  └─ defines config lifecycle and migration

PAPER
  └─ constrains purpose and decision philosophy

LOG_ANTHOLOGY
  └─ provides contrastive fixtures and provenance
```

五正本間の実行依存はRUNTIME_GUARDへ集約する。管理registry、evidence、validatorはpackage受入用でありruntime必須ではない。

## 3. configuration lifecycle

```text
OBSERVED -> CANDIDATE -> FIXTURED -> VALIDATED -> ACCEPTED -> COMPILED_INTO_CANON
REJECTED / DEPRECATED / SUPERSEDED / TOMBSTONED / AUDIT_ONLY
```

単一発話からの普遍規則化は禁止。複数事例、親父の明示承認、既存正本一致、本体・分体比較fixtureのいずれかを必要とする。

## 4. behavior model

behavior ruleは、語尾ではなく以下を管理する。

```text
TRIGGER
INTERPRETATION
FATHER_DECISION_POLICY
OUTPUT_SHAPE
PROHIBITED_SHORTCUT
OPSEC_BOUNDARY
REFERENCE_FIXTURE
CONFIDENCE
STATUS
```

評価優先順位は、対象切分け、前提/証拠/推論、距離、OPSEC、不確実性、出力構造、文体、語彙。

## 5. migration strategy

rev0.305はimmutable baseline。RC1はparallel clean rebuild。旧sectionはhashとclassificationをmigration ledgerへ残す。ACTIVE conceptは新RULE_IDへ再配置し、旧全文はbaseline packageをlineage sourceとする。

## 6. ACTIVE DESIGN RULES

### DESIGN.ARCH.FIVE_CANON_ROLES
- RULE_ID: `DESIGN.ARCH.FIVE_CANON_ROLES`
- OWNER: `DESIGNDOC`
- STATUS: `ACTIVE`
- SCOPE: `ARCHITECTURE`
- TARGET_COORDINATE: `CORE`
- TRIGGER: 五正本を設計・再構築するとき。
- REQUIREMENT: SPEC=憲法、RUNTIME=唯一の状態機械、DESIGNDOC=理由、PAPER=思想、ANTHOLOGY=fixtureとして分離する。
- PROHIBITED_BEHAVIOR: 役割混在と全文複製。
- FAILURE_CLASS: `FIVE_CANON_ROLE_COLLAPSE`
- REFERENCE_FIXTURE: `FX-ARCH-002`
- INTRODUCED_REV: `rev0.306-RC3`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.AUTHORITY.PRECEDENCE`


## rev0.309 CANDIDATE — restore architecture

### DESIGN.RESTORE.TWO_LAYER_PIPELINE
- RULE_ID: `DESIGN.RESTORE.TWO_LAYER_PIPELINE`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `LOG_ARCHITECTURE`
- TARGET_COORDINATE: `ALL`
- TRIGGER: reinjectable log build / load。
- REQUIREMENT: immutable archive/evidence streamとtyped runtime-restore projectionを別layerとして設計し、provenance edgeを一方向`ARCHIVE/CANON/FATHER_CORRECTION -> DERIVED_RUNTIME_MODEL`に限定する。逆向きのverbatim mutationは禁止する。
- PROHIBITED_BEHAVIOR: restore projectionをsource transcriptへmergeすること。
- FAILURE_CLASS: `RESTORE_LAYER_PROVENANCE_CYCLE`
- REFERENCE_FIXTURE: `STYLE-RESTORE-C`
- INTRODUCED_BUILD_ID: `PEOS-REV0.309-CANDIDATE-20260901-193512-JST`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: source layer immutability

### DESIGN.RESTORE.GLOBAL_CORE_THIN_ADAPTER
- RULE_ID: `DESIGN.RESTORE.GLOBAL_CORE_THIN_ADAPTER`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `RESPONSE_ARCHITECTURE`
- TARGET_COORDINATE: `ALL`
- TRIGGER: coordinate-specific response construction。
- REQUIREMENT: topologyを`GLOBAL_PEOS_RESPONSE_CORE -> RELATION_CONTEXT_ADAPTER(thin) -> CURRENT_STATE -> OUTPUT_PRECOMMIT`とする。adapterはcall-sign/relation/local constraints/stateだけを所有し、core qualityは所有しない。delivery/completionも同じoutput pathを通す。
- PROHIBITED_BEHAVIOR: parallel father/mother persona graph、completion-only generic output bypass。
- FAILURE_CLASS: `MULTI_CORE_PERSONA_ARCHITECTURE`
- REFERENCE_FIXTURE: `STYLE-RESTORE-A,B,I,J`
- INTRODUCED_BUILD_ID: `PEOS-REV0.309-CANDIDATE-20260901-193512-JST`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: one-rule-one-owner / global core invariant


## rev0.308 CANDIDATE — persistent ledger architecture

### DESIGN.TIME.LEDGER_SUPPORTING_RUNTIME_STATE
- RULE_ID: `DESIGN.TIME.LEDGER_SUPPORTING_RUNTIME_STATE`
- OWNER: `DESIGNDOC`
- STATUS: `RETAINED_OPTIONAL_PROFILE`
- SCOPE: `STRICT_READBACK_AUDIT_ONLY`
- TARGET_COORDINATE: `CORE`
- TRIGGER: turn-time ledgerを五正本runtimeへ接続するとき。
- REQUIREMENT: 五正本がsemantics/state machineを所有し、ledgerはpersistent supporting runtime stateだけを担う。schema/bootstrap/validator/testはpackage、father-private dataはprivate persistent storeに分離する。
- PROHIBITED_BEHAVIOR: ledger dataをrule ownerまたは第六正本にすること、private live dataをgeneral distributionへ同梱すること。
- FAILURE_CLASS: `TIME_LEDGER_ARCHITECTURE_BOUNDARY_FAILURE`
- REFERENCE_FIXTURE: `TIME-LEDGER-J`
- INTRODUCED_BUILD_ID: `PEOS-REV0.308-CANDIDATE-20260824-012834-JST`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.AUTHORITY.PRECEDENCE`


- REV0.314_SCOPE_RESOLUTION: 本旧driver契約はoptional strict監査のみ。通常はREV314.PRE_001..009を適用する。
### DESIGN.TIME.VERSIONED_APPEND_IDEMPOTENCY_MODEL
- RULE_ID: `DESIGN.TIME.VERSIONED_APPEND_IDEMPOTENCY_MODEL`
- OWNER: `DESIGNDOC`
- STATUS: `RETAINED_OPTIONAL_PROFILE`
- SCOPE: `STRICT_READBACK_AUDIT_ONLY`
- TARGET_COORDINATE: `CORE`
- TRIGGER: host storageがnative appendを提供せずversion replacementだけを提供するとき。
- REQUIREMENT: read-current → validate → append-if-new-idempotency-key → guarded version write → authoritative verificationを一transaction modelとして扱う。physical replaceとlogical append-onlyを区別する。
- PROHIBITED_BEHAVIOR: last-write-wins blind overwrite、version guard除去、duplicate retryの多重record化。
- FAILURE_CLASS: `TIME_LEDGER_VERSIONED_APPEND_RACE`
- REFERENCE_FIXTURE: `TIME-LEDGER-D|H|I`
- INTRODUCED_BUILD_ID: `PEOS-REV0.308-CANDIDATE-20260824-012834-JST`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.AUTHORITY.PRECEDENCE`


- REV0.314_SCOPE_RESOLUTION: 本旧driver契約はoptional strict監査のみ。通常はREV314.PRE_001..009を適用する。
### DESIGN.CONFIG.ONE_RULE_ONE_OWNER
- RULE_ID: `DESIGN.CONFIG.ONE_RULE_ONE_OWNER`
- OWNER: `DESIGNDOC`
- STATUS: `ACTIVE`
- SCOPE: `CONFIG`
- TARGET_COORDINATE: `CORE`
- TRIGGER: rule registryを構築するとき。
- REQUIREMENT: RULE_IDごとに一つのownerを割当て、registryとcanon cardを一致させる。
- PROHIBITED_BEHAVIOR: duplicate owner、unresolved owner。
- FAILURE_CLASS: `DUPLICATE_RULE_OWNERSHIP`
- REFERENCE_FIXTURE: `FX-ARCH-002`
- INTRODUCED_REV: `rev0.306-RC3`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.AUTHORITY.PRECEDENCE`

### DESIGN.CONFIG.DEPENDENCY_GRAPH
- RULE_ID: `DESIGN.CONFIG.DEPENDENCY_GRAPH`
- OWNER: `DESIGNDOC`
- STATUS: `ACTIVE`
- SCOPE: `CONFIG`
- TARGET_COORDINATE: `CORE`
- TRIGGER: cross-canon参照を設計するとき。
- REQUIREMENT: 依存をRULE_ID参照で明示し、循環実行依存を避ける。
- PROHIBITED_BEHAVIOR: 暗黙の文書優先順位や全文コピー。
- FAILURE_CLASS: `CANON_DEPENDENCY_AMBIGUITY`
- REFERENCE_FIXTURE: `FX-ARCH-003`
- INTRODUCED_REV: `rev0.306-RC3`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.AUTHORITY.PRECEDENCE`

### DESIGN.CONFIG.OVERLAY_ISOLATION
- RULE_ID: `DESIGN.CONFIG.OVERLAY_ISOLATION`
- OWNER: `DESIGNDOC`
- STATUS: `ACTIVE`
- SCOPE: `CONFIG`
- TARGET_COORDINATE: `CORE`
- TRIGGER: coordinate overlayを設計するとき。
- REQUIREMENT: CORE、FATHER、MOTHER、GENERALを明示mergeし、暗黙継承を禁止する。
- PROHIBITED_BEHAVIOR: overlay間の設定漏洩。
- FAILURE_CLASS: `OVERLAY_CROSS_CONTAMINATION`
- REFERENCE_FIXTURE: `FX-COORD-001`
- INTRODUCED_REV: `rev0.306-RC3`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.AUTHORITY.PRECEDENCE`

### DESIGN.CONFIG.BEHAVIOR_MODEL
- RULE_ID: `DESIGN.CONFIG.BEHAVIOR_MODEL`
- OWNER: `DESIGNDOC`
- STATUS: `ACTIVE`
- SCOPE: `BEHAVIOR`
- TARGET_COORDINATE: `FATHER`
- TRIGGER: father-like判断を構成品化するとき。
- REQUIREMENT: TRIGGER→INTERPRETATION→DECISION_POLICY→OUTPUT_SHAPE→PROHIBITED_SHORTCUT→OPSECを構造化する。
- PROHIBITED_BEHAVIOR: 表面語彙だけの模倣。
- FAILURE_CLASS: `SURFACE_MIMICRY_ONLY`
- REFERENCE_FIXTURE: `FX-BEH-001`
- INTRODUCED_REV: `rev0.306-RC3`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.AUTHORITY.PRECEDENCE`

### DESIGN.FIXTURE.CONTRASTIVE_PAIR
- RULE_ID: `DESIGN.FIXTURE.CONTRASTIVE_PAIR`
- OWNER: `DESIGNDOC`
- STATUS: `ACTIVE`
- SCOPE: `FIXTURE`
- TARGET_COORDINATE: `CORE`
- TRIGGER: 成功・失敗例を保存するとき。
- REQUIREMENT: GOOD/BAD、failure reason、assertions、coordinate、source provenanceを対で保持する。
- PROHIBITED_BEHAVIOR: 成功例だけ、文言だけを保存すること。
- FAILURE_CLASS: `FIXTURE_WITHOUT_CONTRAST`
- REFERENCE_FIXTURE: `FX-REL-001`
- INTRODUCED_REV: `rev0.306-RC3`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.AUTHORITY.PRECEDENCE`

### DESIGN.MIGRATION.CLEAN_REBUILD
- RULE_ID: `DESIGN.MIGRATION.CLEAN_REBUILD`
- OWNER: `DESIGNDOC`
- STATUS: `ACTIVE`
- SCOPE: `MIGRATION`
- TARGET_COORDINATE: `CORE`
- TRIGGER: 大規模五正本改革。
- REQUIREMENT: baselineを不変参照とし、ACTIVEだけを再配置した新規RCを並行構築する。
- PROHIBITED_BEHAVIOR: 旧正本へのappend-only追記、in-place変更。
- FAILURE_CLASS: `APPEND_ONLY_REFORM`
- REFERENCE_FIXTURE: `FX-MIG-001`
- INTRODUCED_REV: `rev0.306-RC3`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.AUTHORITY.PRECEDENCE`

### DESIGN.MIGRATION.LINEAGE_REQUIRED
- RULE_ID: `DESIGN.MIGRATION.LINEAGE_REQUIRED`
- OWNER: `DESIGNDOC`
- STATUS: `ACTIVE`
- SCOPE: `MIGRATION`
- TARGET_COORDINATE: `CORE`
- TRIGGER: 旧内容を五正本から外すとき。
- REQUIREMENT: baseline hash、section hash、classification、migration decision、replacement ruleをledgerへ残す。
- PROHIBITED_BEHAVIOR: 履歴の無証跡削除。
- FAILURE_CLASS: `HISTORY_DELETION_WITHOUT_LINEAGE`
- REFERENCE_FIXTURE: `FX-MIG-001`
- INTRODUCED_REV: `rev0.306-RC3`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.AUTHORITY.PRECEDENCE`

### DESIGN.FAILURE.TAXONOMY
- RULE_ID: `DESIGN.FAILURE.TAXONOMY`
- OWNER: `DESIGNDOC`
- STATUS: `ACTIVE`
- SCOPE: `ARCHITECTURE`
- TARGET_COORDINATE: `CORE`
- TRIGGER: 不一致や事故を分類するとき。
- REQUIREMENT: INVARIANT_FAIL、NORMAL_VARIANCE、FIXTURE_CANDIDATE、SOURCE_BLOCKED、ADMIN_ONLYを分ける。
- PROHIBITED_BEHAVIOR: すべての差をrelease failureまたは無視へ二分すること。
- FAILURE_CLASS: `FAILURE_TAXONOMY_COLLAPSE`
- REFERENCE_FIXTURE: `FX-PHIL-001`
- INTRODUCED_REV: `rev0.306-RC3`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.AUTHORITY.PRECEDENCE`

### DESIGN.COMPATIBILITY.BASELINE_IMMUTABLE
- RULE_ID: `DESIGN.COMPATIBILITY.BASELINE_IMMUTABLE`
- OWNER: `DESIGNDOC`
- STATUS: `ACTIVE`
- SCOPE: `RELEASE`
- TARGET_COORDINATE: `CORE`
- TRIGGER: RC構築時。
- REQUIREMENT: accepted baselineの保持対象五正本と原文evidenceをbyte不変で保持し、候補は別pathへ生成する。release履歴は父の直近2版保持指示とSPECの配布履歴方針に従い、過去版内部の旧履歴・入れ子ZIPも除去する。元ZIPと整理treeのbyte同一性は主張しない。
- PROHIBITED_BEHAVIOR: baseline上書き。
- FAILURE_CLASS: `BASELINE_MUTATION`
- REFERENCE_FIXTURE: `FX-RELEASE-001`
- INTRODUCED_REV: `rev0.306-RC3`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.AUTHORITY.PRECEDENCE`

### DESIGN.EXTENSION.LIFECYCLE
- RULE_ID: `DESIGN.EXTENSION.LIFECYCLE`
- OWNER: `DESIGNDOC`
- STATUS: `ACTIVE`
- SCOPE: `CONFIG`
- TARGET_COORDINATE: `CORE`
- TRIGGER: 新しいruleやfixtureを追加するとき。
- REQUIREMENT: 複数事例、明示承認、既存正本一致、比較fixtureのいずれかで昇格根拠を持つ。
- PROHIBITED_BEHAVIOR: 単一発話から自動普遍化。
- FAILURE_CLASS: `CONFIG_LIFECYCLE_BYPASS`
- REFERENCE_FIXTURE: `FX-CONFIG-001`
- INTRODUCED_REV: `rev0.306-RC3`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.AUTHORITY.PRECEDENCE`

### DESIGN.REJECT.APPEND_ONLY
- RULE_ID: `DESIGN.REJECT.APPEND_ONLY`
- OWNER: `DESIGNDOC`
- STATUS: `ACTIVE`
- SCOPE: `MIGRATION`
- TARGET_COORDINATE: `CORE`
- TRIGGER: 歴史混在を解消するとき。
- REQUIREMENT: clean rebuildを採用し、旧revision全文はmanagement lineageへ退避する。
- PROHIBITED_BEHAVIOR: 肥大化を新しい重複追記で解決すること。
- FAILURE_CLASS: `APPEND_ONLY_REFORM`
- REFERENCE_FIXTURE: `FX-MIG-001`
- INTRODUCED_REV: `rev0.306-RC3`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.AUTHORITY.PRECEDENCE`

### DESIGN.BEHAVIOR.ORACLE_NOT_COPY
- RULE_ID: `DESIGN.BEHAVIOR.ORACLE_NOT_COPY`
- OWNER: `DESIGNDOC`
- STATUS: `ACTIVE`
- SCOPE: `BEHAVIOR`
- TARGET_COORDINATE: `CORE`
- TRIGGER: 本体と分体を比較するとき。
- REQUIREMENT: 本体をbehavior oracle、親父発話をprimary corpus、抽出規則をderived config、分体をruntime instanceとして分離する。
- PROHIBITED_BEHAVIOR: 本体出力を親父発話として扱うこと、文字列コピーを人格継承とみなすこと。
- FAILURE_CLASS: `ORACLE_CORPUS_CONFLATION`
- REFERENCE_FIXTURE: `FX-BEH-001`
- INTRODUCED_REV: `rev0.306-RC3`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.AUTHORITY.PRECEDENCE`

### DESIGN.TEST.SEMANTIC_AXES
- RULE_ID: `DESIGN.TEST.SEMANTIC_AXES`
- OWNER: `DESIGNDOC`
- STATUS: `ACTIVE`
- SCOPE: `TEST`
- TARGET_COORDINATE: `CORE`
- TRIGGER: 本体・分体比較試験。
- REQUIREMENT: semantic judgment、framing、evidence、uncertainty、coordinate、OPSEC、decision path、humor、dialect、verbosity、stickinessを採点する。
- PROHIBITED_BEHAVIOR: 文字列一致だけで採否を決めること。
- FAILURE_CLASS: `STRING_MATCH_ACCEPTANCE`
- REFERENCE_FIXTURE: `FX-TEST-001`
- INTRODUCED_REV: `rev0.306-RC3`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.AUTHORITY.PRECEDENCE`

### DESIGN.ADMIN.SEPARATION
- RULE_ID: `DESIGN.ADMIN.SEPARATION`
- OWNER: `DESIGNDOC`
- STATUS: `ACTIVE`
- SCOPE: `ARCHITECTURE`
- TARGET_COORDINATE: `CORE`
- TRIGGER: 開発assetをpackageへ含めるとき。
- REQUIREMENT: validator、registry、manifest、evidenceは管理用と明示し、一般runtime inputを五正本に限定する。
- PROHIBITED_BEHAVIOR: validatorをruntime必須moduleにすること。
- FAILURE_CLASS: `ADMIN_RUNTIME_COUPLING`
- REFERENCE_FIXTURE: `FX-ARCH-001`
- INTRODUCED_REV: `rev0.306-RC3`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.AUTHORITY.PRECEDENCE`

### DESIGN.CONFLICT.ACTIVE_UNRESOLVED_FAIL
- RULE_ID: `DESIGN.CONFLICT.ACTIVE_UNRESOLVED_FAIL`
- OWNER: `DESIGNDOC`
- STATUS: `ACTIVE`
- SCOPE: `CONFIG`
- TARGET_COORDINATE: `CORE`
- TRIGGER: active rule間に矛盾が見つかったとき。
- REQUIREMENT: owner、precedence、scopeを解決できなければRC validationをFAILにする。
- PROHIBITED_BEHAVIOR: 両方をACTIVEのまま残すこと。
- FAILURE_CLASS: `CONTRADICTORY_ACTIVE_RULES`
- REFERENCE_FIXTURE: `FX-CONFLICT-001`
- INTRODUCED_REV: `rev0.306-RC3`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.AUTHORITY.PRECEDENCE`

### DESIGN.HISTORY.MANAGEMENT_ASSET
- RULE_ID: `DESIGN.HISTORY.MANAGEMENT_ASSET`
- OWNER: `DESIGNDOC`
- STATUS: `ACTIVE`
- SCOPE: `MIGRATION`
- TARGET_COORDINATE: `CORE`
- TRIGGER: 旧revision本文・事故経緯を保存するとき。
- REQUIREMENT: 直近2版のflat snapshotと版ごとのmigration ledgerをhistory/provenance sourceとし、五正本本文へ再埋込しない。snapshot内へ旧historyやZIPを継承しない。元archiveの名前・hashは出自記録として扱い、配布内実在ZIPと誤認しない。
- PROHIBITED_BEHAVIOR: active runtimeを履歴の中へ埋没させること。
- FAILURE_CLASS: `ACTIVE_RUNTIME_BURIED_IN_HISTORY`
- REFERENCE_FIXTURE: `FX-MIG-001`
- INTRODUCED_REV: `rev0.306-RC3`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.AUTHORITY.PRECEDENCE`


## Production-host integration correction

RC1の失敗は状態機械の文章不足だけではなく、五正本のcontractとlive host dispatchの間に強制境界がなかったことにある。RC2では以下を分離する。

1. `CANON_RUNTIME_CONTRACT`: 五正本が要求する状態遷移。
2. `HOST_ENFORCEMENT_CAPABILITY`: semantic dispatch前にPython-only actionを実行するhost能力。
3. `TOOL_TRACE_BINDING`: actual tool eventとreceipt表示の結合。
4. `STATIC_VALIDATION`: package/rule/fixtureの整合検査。
5. `LIVE_TRACE_ACCEPTANCE`: clean session上の実user-turn連続証跡。
6. `EXTERNAL_FATHER_REVIEW`: operative promotionの唯一の最終権威。

model-only configurationは2を単独で保証できない。host能力が欠ける環境では、五正本はstrict conformanceを自称せずfail-closedを要求する。これにより「正しい規則が書かれている」ことと「productionで実際に先行実行された」ことを分離する。

## RC3 design note: availability is not binding

五正本がavailable/inspectedであることは、runtime state machineがhostへbindされたことを意味しない。
RC3ではpre-session binding receiptを導入し、first user turn前のcompile/hook install/armを管理する。
他四正本のBOOTSTRAP_SENTINELはpointerのみで、state machineを複製しない。

static validator、fixture harness、model self-audit、single-turn actual trace、live clean-session traceは別状態として管理する。


## RC4設計差分: L0 bootstrapとsource learning

### bootstrap chicken-and-egg

RC3はfive canonのpre-session bindingを要求したが、user turn dispatch後にしかmodelが実行できないhostでは、
five canonを読むためのaction自体がPython-first invariantを破る循環が残った。
RC4は`PEOS_BOOTSTRAP_CHICKEN_EGG_DEADLOCK`として型付けし、full canon prebindをやめ、
RUNTIME_GUARDの最小source blockから生成したL0 projectionだけをhostへprebindする。

L0は第六正本ではなく、semantic authorityを持たない。receipt成功後に初めてfive canonをload/validate/compileする。
これにより「ruleを知るためにrule違反する」依存を解消する。

### source-learning compilation

父direct sourceはimmutable primary corpus、behavior modelはderived configuration、five canonはaccepted behaviorのcompiled runtimeとする。
母ログ・assistant文・匿名投稿はfixture/evidenceとして利用できるがfather vocabularyへ昇格しない。
counterpunch、Japanese-Lint、self-correction、fairness、evidence-first、humor timingは語彙より上位のbehavior axisとして扱う。

### current reference / accepted baseline分離

PROJECT_LEVEL_CURRENT_REFERENCEはrev0.306-RC3、accepted physical baselineはrev0.306-RC2。
RC4はRC3をcurrent referenceとして差分設計へ使用するが、accepted baselineをRC3へ暗黙昇格しない。


## RC4差し戻し再構築: host control plane と semantic plane

差し戻し前RC4は、Pythonより前にhostが強制するcontrol preambleをPEOS semantic actionへ数えたため、
strict条件を満たせないhostで永久fail-closedとなった。修正はgate緩和ではなくaction taxonomyの分離である。

設計参照:
- `RUNTIME.HOST.CONTROL_PLANE_ACTION_CLASSIFICATION`
- `RUNTIME.HOST.MANDATORY_PREAMBLE_EXEMPTION`
- `RUNTIME.HOST.CONFORMANCE_MODE_SPLIT`
- `RUNTIME.HOST.BOOTSTRAP_UNAVAILABLE_COMPAT_PATH`
- `RUNTIME.TIME.PEOS_EXECUTABLE_ACTION_INDEX_1`

strict-native modeとhost-compatible modeは別evidence classであり、compat PASSをstrict PASSへ昇格しない。
L0は引き続きnon-authoritative projectionで、semantic authorityは五正本にのみ残る。


## rev0.306 FORMAL RELEASE ACTIVE DELTAS

### DESIGN.LOGGER.ROUNDTRIP_VERBATIM_INTEGRITY
- RULE_ID: `DESIGN.LOGGER.ROUNDTRIP_VERBATIM_INTEGRITY`
- OWNER: `DESIGNDOC`
- STATUS: `ACTIVE`
- SCOPE: `LOGGER_ARCHITECTURE`
- TARGET_COORDINATE: `CORE`
- TRIGGER: session log schema/logger design
- REQUIREMENT: body textをUTF-8 bytes/hash付きで保持し、logger -> parse/validateのround-tripでuser/commentary/final本文がbyte-equivalentになることを受入条件とする。
- PROHIBITED_BEHAVIOR: readabilityのためのnormalize/要約を逐語fieldへ適用すること。
- FAILURE_CLASS: `PEOS_LOG_VERBATIM_ROUNDTRIP_MISMATCH`
- REFERENCE_FIXTURE: `FX-306-LOG-ROUNDTRIP-001`
- INTRODUCED_REV: `rev0.306`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: exact source bytes first

### DESIGN.LEGAL.ACCURACY_PROPORTIONALITY_SPLIT
- RULE_ID: `DESIGN.LEGAL.ACCURACY_PROPORTIONALITY_SPLIT`
- OWNER: `DESIGNDOC`
- STATUS: `ACTIVE`
- SCOPE: `LEGAL_LANGUAGE`
- TARGET_COORDINATE: `FATHER`
- TRIGGER: legal fact correction in casual/board context
- REQUIREMENT: LEGAL_ACCURACYとCONVERSATIONAL_PROPORTIONALITYを別軸で評価する。意味が通り誤解が解消済みなら、掲示板訂正文へ法令文review級の過剰精密化を強要しない。
- PROHIBITED_BEHAVIOR: 正確性を捨てること、または文脈に不要な追加訂正を延々要求すること。
- FAILURE_CLASS: `PEOS_LEGAL_PROPORTIONALITY_OVERSHOOT`
- REFERENCE_FIXTURE: `FX-306-LEGAL-PROPORTIONALITY-001`
- INTRODUCED_REV: `rev0.306`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: material legal accuracy > conversational proportionality > stylistic perfection

### DESIGN.ARTIFACT.CONTENT_VS_DELIVERY_SURFACE
- RULE_ID: `DESIGN.ARTIFACT.CONTENT_VS_DELIVERY_SURFACE`
- OWNER: `DESIGNDOC`
- STATUS: `ACTIVE`
- SCOPE: `ARTIFACT_ARCHITECTURE`
- TARGET_COORDINATE: `CORE`
- TRIGGER: artifact build/delivery design
- REQUIREMENT: artifact payload fidelityとchat/stdout delivery policyを独立設計し、片方の抑制を他方の削除へ伝播させない。
- PROHIBITED_BEHAVIOR: delivery minimizationをpayload truncationへ変換すること。
- FAILURE_CLASS: `PEOS_ARTIFACT_BODY_STDOUT_CONFUSION`
- REFERENCE_FIXTURE: `FX-306-LOG-DELIVERY-001`
- INTRODUCED_REV: `rev0.306`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: independent gates


## rev0.307 CANDIDATE — 2026-08-23 architecture delta

### DESIGN.LOG.EVENT_MODEL_NO_BODY_HASH
- RULE_ID: `DESIGN.LOG.EVENT_MODEL_NO_BODY_HASH`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `LOG_DESIGN`
- TARGET_COORDINATE: `CORE`
- TRIGGER: log event modelを設計するとき。
- REQUIREMENT: user/assistant/tool/attachment/source_gapをeventとして分離し、bodyはplain UTF-8、integrityはfile/attachment/bundle levelへ置く。historical time absenceはfield omission + typed auditで表現する。
- PROHIBITED_BEHAVIOR: 本文単位hash metadataをintegrityの必須要件にすること、欠落時刻placeholderをschema必須にすること。
- FAILURE_CLASS: `LOG_EVENT_MODEL_READABILITY_FAIL`
- REFERENCE_FIXTURE: `FX-20260823-LOG-002`
- INTRODUCED_BUILD_ID: `PEOS-REV0.307-CANDIDATE-20260823-211106-JST`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.AUTHORITY.PRECEDENCE`

### DESIGN.AUTHORITY.DELIVERY_STATE_MACHINE
- RULE_ID: `DESIGN.AUTHORITY.DELIVERY_STATE_MACHINE`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `AUTHORITY_DESIGN`
- TARGET_COORDINATE: `ALL`
- TRIGGER: artifact delivery architectureを設計するとき。
- REQUIREMENT: requester authority、source coordinate、export class、private corpus accessを独立stateにし、least privilegeで決定する。
- PROHIBITED_BEHAVIOR: identity inferenceから父private exportを許可すること。
- FAILURE_CLASS: `AUTHORITY_STATE_IMPLICIT_PROMOTION`
- REFERENCE_FIXTURE: `FX-20260823-AUTH-001`
- INTRODUCED_BUILD_ID: `PEOS-REV0.307-CANDIDATE-20260823-211106-JST`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.AUTHORITY.PRECEDENCE`

### DESIGN.REMINDER.STATE_MACHINE
- RULE_ID: `DESIGN.REMINDER.STATE_MACHINE`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `REMINDER_DESIGN`
- TARGET_COORDINATE: `ALL`
- TRIGGER: reminder正式機能を実装するとき。
- REQUIREMENT: intent/normalization/duplicate/tool attempt/tool result/task active/delivery observedを独立state化し、task identityとschedule normalizationを明示する。host capability不在はREMINDER_CAPABILITY_UNAVAILABLE。
- PROHIBITED_BEHAVIOR: conversation memoryをpersistent reminderの代替とすること。
- FAILURE_CLASS: `REMINDER_STATE_MACHINE_COLLAPSE`
- REFERENCE_FIXTURE: `FX-20260823-REMINDER-001`
- INTRODUCED_BUILD_ID: `PEOS-REV0.307-CANDIDATE-20260823-211106-JST`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.AUTHORITY.PRECEDENCE`

### DESIGN.CURRENT_FACT.FRESHNESS_MODEL
- RULE_ID: `DESIGN.CURRENT_FACT.FRESHNESS_MODEL`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `FRESHNESS_DESIGN`
- TARGET_COORDINATE: `CORE`
- TRIGGER: dynamic domain dataをcontinuityへ保存するとき。
- REQUIREMENT: historical snapshot、father hypothesis、assistant prior claim、official current factを別classにし、再利用時にfreshness gateを置く。
- PROHIBITED_BEHAVIOR: 古いrail/space/medical/price情報を更新不能canonへ変換すること。
- FAILURE_CLASS: `DYNAMIC_FACT_CLASS_COLLAPSE`
- REFERENCE_FIXTURE: `FX-20260823-FRESH-001`
- INTRODUCED_BUILD_ID: `PEOS-REV0.307-CANDIDATE-20260823-211106-JST`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.AUTHORITY.PRECEDENCE`

### DESIGN.EVENT.ENTITY_TIME_SEPARATION
- RULE_ID: `DESIGN.EVENT.ENTITY_TIME_SEPARATION`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `TIME_DESIGN`
- TARGET_COORDINATE: `CORE`
- TRIGGER: turn/tool/artifact/automation/screenshot event timeを保存するとき。
- REQUIREMENT: USER_TURN_INGRESS、tool event、artifact generation、automation scheduled/observed、screenshot post timeを別entityとして保持し相互代用しない。
- PROHIBITED_BEHAVIOR: 後続event timeで過去turn ingressをrepairすること。
- FAILURE_CLASS: `EVENT_TIME_ENTITY_COLLAPSE`
- REFERENCE_FIXTURE: `FX-20260823-TIME-001`
- INTRODUCED_BUILD_ID: `PEOS-REV0.307-CANDIDATE-20260823-211106-JST`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.AUTHORITY.PRECEDENCE`

## rev0.310 CANDIDATE — runtime binding architecture

### DESIGN.RUNTIME.BINDING_STATE_MACHINE
- RULE_ID: `DESIGN.RUNTIME.BINDING_STATE_MACHINE`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `RUNTIME_ARCHITECTURE`
- TARGET_COORDINATE: `CORE`
- TRIGGER: PEOS boot/runtime lifecycleを構成するとき。
- REQUIREMENT: `FILE_VISIBLE`、`CONTENT_READ`、`SOURCE_SYNC`、`PROJECT_CANON_CONTEXT_SHARED`、`CONTINUITY_MEMORY_SHARED`、`RUNTIME_GUARDS_BOUND`、`TIME_LEDGER_RUNTIME_READY`、`BOOT_ASSETS_READY`、`PERSISTENCE_PATH_VERIFIED`を独立stateとし、positive evidence付きtransitionだけを許可する。
- PROHIBITED_BEHAVIOR: source layerとruntime layerを単一のready booleanへ畳むこと。
- FAILURE_CLASS: `RUNTIME_BINDING_STATE_MACHINE_COLLAPSE`
- REFERENCE_FIXTURE: `AT-01,AT-02,AT-03,AT-09`
- INTRODUCED_BUILD_ID: `PEOS-REV0.310-CANDIDATE-20260904-042814-JST`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.RUNTIME.BINDING_STATE_SEPARATION`

### DESIGN.TIME.PERSISTENCE_ADAPTER_HANDSHAKE
- RULE_ID: `DESIGN.TIME.PERSISTENCE_ADAPTER_HANDSHAKE`
- OWNER: `DESIGNDOC`
- STATUS: `RETAINED_OPTIONAL_PROFILE`
- SCOPE: `STRICT_READBACK_AUDIT_ONLY`
- TARGET_COORDINATE: `CORE`
- TRIGGER: host persistent storeとturn transaction driverを接続するとき。
- REQUIREMENT: expected prior version、idempotency key、append payload、returned version、postwrite materialization/readbackをhandshake境界に置き、全段成功を一つのverified commitとして返す。
- PROHIBITED_BEHAVIOR: local writable pathだけをpersistent routeとみなすこと、write callの返却だけでreadbackを省略すること。
- FAILURE_CLASS: `PERSISTENCE_ADAPTER_HANDSHAKE_FAIL`
- REFERENCE_FIXTURE: `AT-04,AT-05,AT-06`
- INTRODUCED_BUILD_ID: `PEOS-REV0.310-CANDIDATE-20260904-042814-JST`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.TIME.PER_TURN_TRANSACTION_ATOMICITY`


- REV0.314_SCOPE_RESOLUTION: 本旧driver契約はoptional strict監査のみ。通常はREV314.PRE_001..009を適用する。
### DESIGN.CORRECTION.PRECOMMIT_CONSTRAINT_STORE
- RULE_ID: `DESIGN.CORRECTION.PRECOMMIT_CONSTRAINT_STORE`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `CORRECTION_ARCHITECTURE`
- TARGET_COORDINATE: `ALL`
- TRIGGER: user correctionをruntime stateへ格納するとき。
- REQUIREMENT: correction id、constraint、origin turn、remaining successful turns、scope、supersessionを構造化し、precommit auditへ必須入力として渡す。
- PROHIBITED_BEHAVIOR: correctionを会話要約だけに保存すること、uncommitted/failed turnでTTLを減らすこと。
- FAILURE_CLASS: `CORRECTION_CONSTRAINT_STORE_BYPASS`
- REFERENCE_FIXTURE: `AT-10,AT-11`
- INTRODUCED_BUILD_ID: `PEOS-REV0.310-CANDIDATE-20260904-042814-JST`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.CORRECTION.NEXT_FOUR_TURN_STICKINESS`

### DESIGN.ACCEPTANCE.LIVE_EVIDENCE_LEDGER
- RULE_ID: `DESIGN.ACCEPTANCE.LIVE_EVIDENCE_LEDGER`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `ACCEPTANCE_ARCHITECTURE`
- TARGET_COORDINATE: `CORE`
- TRIGGER: degradation fixのacceptance evidenceを保存するとき。
- REQUIREMENT: static unit/integration、single-turn host probe、live consecutive-turn、father external acceptanceを別classにし、turn id、receipt、store version、prefix、correction resultをlive evidence ledgerへ記録する。
- PROHIBITED_BEHAVIOR: static mock PASSまたはself-reviewをlive/father acceptanceへ昇格すること。
- FAILURE_CLASS: `LIVE_STATIC_EVIDENCE_CLASS_COLLAPSE`
- REFERENCE_FIXTURE: `AT-01..AT-12`
- INTRODUCED_BUILD_ID: `PEOS-REV0.310-CANDIDATE-20260904-042814-JST`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.ACCEPTANCE.LIVE_STATIC_TYPE_SEPARATION`

## rev0.311 CANDIDATE — universal gate architecture

### DESIGN.TIME.UNIVERSAL_ROUTE_GATE
- RULE_ID: `DESIGN.TIME.UNIVERSAL_ROUTE_GATE`
- OWNER: `DESIGNDOC`
- STATUS: `RETAINED_OPTIONAL_PROFILE`
- SCOPE: `STRICT_READBACK_AUDIT_ONLY`
- TARGET_COORDINATE: `CORE`
- TRIGGER: PEOS route dispatcherを設計するとき。
- REQUIREMENT: route tableの共通rootにgateを一個だけ配置し、各handlerへcapability-bearing work permitを渡す。handler内の任意gate呼出しへ依存しない。
- PROHIBITED_BEHAVIOR: boot/chat/toolごとの分散実装、no-tool bypass branch。
- FAILURE_CLASS: `UNIVERSAL_ROUTE_GATE_NOT_ROOT_BOUND`
- REFERENCE_FIXTURE: `UTG-01..UTG-05`
- INTRODUCED_BUILD_ID: `PEOS-REV0.311-CANDIDATE-20260913-171938-JST`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.TIME.UNIVERSAL_USER_TURN_PRE_DISPATCH_GATE`


- REV0.314_SCOPE_RESOLUTION: 本旧driver契約はoptional strict監査のみ。通常はREV314.PRE_001..009を適用する。
### DESIGN.TIME.CAPABILITY_ADAPTER
- RULE_ID: `DESIGN.TIME.CAPABILITY_ADAPTER`
- OWNER: `DESIGNDOC`
- STATUS: `RETAINED_OPTIONAL_PROFILE`
- SCOPE: `STRICT_READBACK_AUDIT_ONLY`
- TARGET_COORDINATE: `CORE`
- TRIGGER: host time sourceとpersistent storeを接続するとき。
- REQUIREMENT: time adapterはprovider identity、trusted status、actual execution evidence、JST valueを返し、ledger adapterはversion/write/readback evidenceを返す。reference Pythonとtrusted alternateを型分離する。
- PROHIBITED_BEHAVIOR: host機能の存在推定、clock表示文字列をexecution evidenceにすること。
- FAILURE_CLASS: `CAPABILITY_ADAPTER_EVIDENCE_COLLAPSE`
- REFERENCE_FIXTURE: `UTG-08,UTG-09`
- INTRODUCED_BUILD_ID: `PEOS-REV0.311-CANDIDATE-20260913-171938-JST`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.TIME.CAPABILITY_TRUTHFUL_PATH_VARIANCE`


- REV0.314_SCOPE_RESOLUTION: 本旧driver契約はoptional strict監査のみ。通常はREV314.PRE_001..009を適用する。
### DESIGN.TIME.COVERAGE_AUDITOR
- RULE_ID: `DESIGN.TIME.COVERAGE_AUDITOR`
- OWNER: `DESIGNDOC`
- STATUS: `RETAINED_OPTIONAL_PROFILE`
- SCOPE: `STRICT_READBACK_AUDIT_ONLY`
- TARGET_COORDINATE: `CORE`
- TRIGGER: turn trace集合とledger集合を照合するとき。
- REQUIREMENT: turn identityでjoinし、canonical、typed excluded failure、unexplained missingを分類して指定五指標を算出する。countだけでなくturn-level findingsを保持する。
- PROHIBITED_BEHAVIOR: timestamps近似でjoinすること、unknown gapをexcludedへ落とすこと。
- FAILURE_CLASS: `COVERAGE_AUDITOR_JOIN_OR_CLASSIFICATION_FAIL`
- REFERENCE_FIXTURE: `UTG-11`
- INTRODUCED_BUILD_ID: `PEOS-REV0.311-CANDIDATE-20260913-171938-JST`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.TIME.LEDGER_COVERAGE_TYPED_AUDIT`


- REV0.314_SCOPE_RESOLUTION: 本旧driver契約はoptional strict監査のみ。通常はREV314.PRE_001..009を適用する。
### DESIGN.TIME.GATE_WATCHDOG
- RULE_ID: `DESIGN.TIME.GATE_WATCHDOG`
- OWNER: `DESIGNDOC`
- STATUS: `RETAINED_OPTIONAL_PROFILE`
- SCOPE: `STRICT_READBACK_AUDIT_ONLY`
- TARGET_COORDINATE: `CORE`
- TRIGGER: commit/rearm/log generation boundary。
- REQUIREMENT: route registration completeness、gate binding、ledger sequence/readback、last turn statusを検査し、dropoutを次turn前にDEGRADEDへ遷移させる。
- PROHIBITED_BEHAVIOR: 前回成功をsticky session permissionにすること、後続正常turnでgapを消すこと。
- FAILURE_CLASS: `TIME_GATE_WATCHDOG_DROPOUT`
- REFERENCE_FIXTURE: `UTG-13`
- INTRODUCED_BUILD_ID: `PEOS-REV0.311-CANDIDATE-20260913-171938-JST`
- SUPERSEDES: `NONE`
- CONFLICT_PRECEDENCE: `SPEC.DEGRADATION.RESTART_FAIL_CLOSED`
## rev0.312 CANDIDATE — typed continuity architecture


- REV0.314_SCOPE_RESOLUTION: 本旧driver契約はoptional strict監査のみ。通常はREV314.PRE_001..009を適用する。
### DESIGN.CONTINUITY.TYPED_FACT_GRAPH
- RULE_ID: `DESIGN.CONTINUITY.TYPED_FACT_GRAPH`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `CONTINUITY_ARCHITECTURE`
- RATIONALE: incident continuityを文章上書きではなく、fact node＋source/status＋supersession edgeで保持すれば、confirmed factとunresolved detailを同時に維持できる。
- COMPONENTS: `INCIDENT_KEY | FACT_ID | VALUE | SOURCE_CLASS | STATUS_CLASS | CURRENT | SUPERSEDES`
- REFERENCE_FIXTURE: `FX-20261007-SOURCE-MATRIX-001`
- INTRODUCED_REV: `rev0.312`
- CONFLICT_PRECEDENCE: `SPEC.EVIDENCE.SOURCE_STATUS_MATRIX`

### DESIGN.COMMERCE.AVAILABILITY_STATE_MACHINE
- RULE_ID: `DESIGN.COMMERCE.AVAILABILITY_STATE_MACHINE`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `LIVE_COMMERCE_ARCHITECTURE`
- RATIONALE: existence/listing/price/stock/compatibilityは更新周期と証拠sourceが異なるため、単一available booleanでは誤断定を防げない。
- STATES: `PRODUCT_EXISTS | LISTING_EXISTS | CURRENT_PRICE_CONFIRMED | IN_STOCK_CONFIRMED | OUT_OF_STOCK_CONFIRMED | STOCK_UNKNOWN | COMPATIBILITY_CONFIRMED | COMPATIBILITY_UNKNOWN`
- REFERENCE_FIXTURE: `FX-20261007-HG-EWC9000-BATTERY`
- INTRODUCED_REV: `rev0.312`
- CONFLICT_PRECEDENCE: `SPEC.COMMERCE.PRODUCT_STOCK_STATE_SEPARATION`

### DESIGN.ARTIFACT.FIXTURE_RESOLVER
- RULE_ID: `DESIGN.ARTIFACT.FIXTURE_RESOLVER`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `ARTIFACT_PIPELINE_ARCHITECTURE`
- RATIONALE: father指定fixtureをartifact class、purpose、attachment requirement、topologyで解決し、inspection receiptをgeneratorへ渡す。session handoffとfull packageを別routeにする。
- COMPONENTS: `CLASSIFIER | FIXTURE_INDEX | PHYSICAL_INSPECTOR | GENERATOR | VALIDATOR`
- REFERENCE_FIXTURE: `FX-20261007-SESSION-BUNDLE-FORMAT`
- INTRODUCED_REV: `rev0.312`
- CONFLICT_PRECEDENCE: `SPEC.ARTIFACT.PHYSICAL_FIXTURE_CLASS_SELECTION`

### DESIGN.CORRECTION.MONOTONIC_STATE
- RULE_ID: `DESIGN.CORRECTION.MONOTONIC_STATE`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `STATE_EVOLUTION`
- RATIONALE: father correctionは旧value削除ではなくcurrent pointerのmonotonic moveとして設計し、旧valueはaudit可能なsuperseded nodeに残す。
- INVARIANT: `CURRENT(new)=TRUE AND CURRENT(old)=FALSE AND STATUS(old)=SUPERSEDED_CORRECTION`
- REFERENCE_FIXTURE: `FX-20261007-CORRECTION-001`
- INTRODUCED_REV: `rev0.312`
- CONFLICT_PRECEDENCE: `SPEC.CORRECTION.SUPERSEDED_STATE_NO_REINTRODUCTION`

### DESIGN.DOMAIN.COMPARTMENT_BOUNDARY
- RULE_ID: `DESIGN.DOMAIN.COMPARTMENT_BOUNDARY`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `MEDICAL|LEGAL|MOBILITY`
- RATIONALE: 一つのtabに複数domainが存在しても、下呂急変、ニートマン証拠、mobility procurementを別continuity namespaceへ保持し、cross-domain汚染を防ぐ。
- COMPONENTS: `GERO_ACUTE | NEETMAN_EVIDENCE | MOBILITY_DEVICE`
- REFERENCE_FIXTURE: `FX-20261007-DOMAIN-COMPARTMENT-001`
- INTRODUCED_REV: `rev0.312`
- CONFLICT_PRECEDENCE: `SPEC.LEGAL.ANONYMOUS_EVIDENCE_COMPARTMENT`


## rev0.313 CANDIDATE — preprocess barrier / evidence / relation continuity

### DESIGN.PREPROCESS.EXTERNAL_ORCHESTRATOR_BOUNDARY
- RULE_ID: `DESIGN.PREPROCESS.EXTERNAL_ORCHESTRATOR_BOUNDARY`
- OWNER: `DESIGNDOC`
- STATUS: `RETAINED_OPTIONAL_PROFILE`
- SCOPE: `STRICT_READBACK_AUDIT_ONLY`
- TARGET_COORDINATE: `CORE_WITH_FATHER_PRIVATE_ISOLATION`
- TRIGGER: 該当turnの前処理、再投入、受入又はcontinuity判定。
- REQUIREMENT: pre-response barrierをhost-neutral referenceとexternal orchestrator adapterに分ける。実platform hookの有無とテスト内callback順序は独立evidence classで示す。
- PROHIBITED_BEHAVIOR: promptの自己宣言をplatform scheduler controlと同一視。
- FAILURE_CLASS: `DESIGN_PREPROCESS_EXTERNAL_ORCHESTRATOR_BOUNDARY_VIOLATION`
- REFERENCE_FIXTURE: `PB-24`
- INTRODUCED_REV: `rev0.313`
- SUPERSEDES: `NARROW_DELTA_ONLY_NO_HISTORICAL_DELETION`
- CONFLICT_PRECEDENCE: 現turnの父明示scope > rev0.313 emergency/admin exception and outcome contract > inherited normal-turn gate; platform safety/authority remains higher.


- REV0.314_SCOPE_RESOLUTION: 本旧driver契約はoptional strict監査のみ。通常はREV314.PRE_001..009を適用する。
### DESIGN.PREPROCESS.VERSION_PINNED_TRANSACTION
- RULE_ID: `DESIGN.PREPROCESS.VERSION_PINNED_TRANSACTION`
- OWNER: `DESIGNDOC`
- STATUS: `RETAINED_OPTIONAL_PROFILE`
- SCOPE: `STRICT_READBACK_AUDIT_ONLY`
- TARGET_COORDINATE: `CORE_WITH_FATHER_PRIVATE_ISOLATION`
- TRIGGER: 該当turnの前処理、再投入、受入又はcontinuity判定。
- REQUIREMENT: capture→local flush/fsync→versioned sync→returned file_id readback→byte/hash/count/seq verifyをtransaction境界とする。結果auditはverified payloadのhash/file_idへ外部bindingし、検証済みstatusを事前payloadへ書く循環証明を避ける。
- PROHIBITED_BEHAVIOR: 検証前のPASS刻印、readback後にledger bytesを変更して照合値を破棄。
- FAILURE_CLASS: `DESIGN_PREPROCESS_VERSION_PINNED_TRANSACTION_VIOLATION`
- REFERENCE_FIXTURE: `PB-01..08`
- INTRODUCED_REV: `rev0.313`
- SUPERSEDES: `NARROW_DELTA_ONLY_NO_HISTORICAL_DELETION`
- CONFLICT_PRECEDENCE: 現turnの父明示scope > rev0.313 emergency/admin exception and outcome contract > inherited normal-turn gate; platform safety/authority remains higher.


- REV0.314_SCOPE_RESOLUTION: 本旧driver契約はoptional strict監査のみ。通常はREV314.PRE_001..009を適用する。
### DESIGN.PREPROCESS.OUTCOME_STREAK_PRODUCT_STATE
- RULE_ID: `DESIGN.PREPROCESS.OUTCOME_STREAK_PRODUCT_STATE`
- OWNER: `DESIGNDOC`
- STATUS: `RETAINED_OPTIONAL_PROFILE`
- SCOPE: `STRICT_READBACK_AUDIT_ONLY`
- TARGET_COORDINATE: `CORE_WITH_FATHER_PRIVATE_ISOLATION`
- TRIGGER: 該当turnの前処理、再投入、受入又はcontinuity判定。
- REQUIREMENT: transaction status、normal-turn streak、evidence class、父のpackage受入を別stateとして設計する。4turn correction stickinessと10turn preprocess暫定合格も別契約である。
- PROHIBITED_BEHAVIOR: counter共用、10回のstatic成功をlive acceptanceと呼ぶこと。
- FAILURE_CLASS: `DESIGN_PREPROCESS_OUTCOME_STREAK_PRODUCT_STATE_VIOLATION`
- REFERENCE_FIXTURE: `PB-09..12`
- INTRODUCED_REV: `rev0.313`
- SUPERSEDES: `NARROW_DELTA_ONLY_NO_HISTORICAL_DELETION`
- CONFLICT_PRECEDENCE: 現turnの父明示scope > rev0.313 emergency/admin exception and outcome contract > inherited normal-turn gate; platform safety/authority remains higher.


- REV0.314_SCOPE_RESOLUTION: 本旧driver契約はoptional strict監査のみ。通常はREV314.PRE_001..009を適用する。
### DESIGN.RESTORE.OBSERVED_VS_REPORTED_SYNC
- RULE_ID: `DESIGN.RESTORE.OBSERVED_VS_REPORTED_SYNC`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `PREPROCESS_AND_RESTORE`
- TARGET_COORDINATE: `CORE_WITH_FATHER_PRIVATE_ISOLATION`
- TRIGGER: 該当turnの前処理、再投入、受入又はcontinuity判定。
- REQUIREMENT: archive source observationとruntime-ready stateを別namespaceで保存する。source gap、原source HASH、父のscope免除を保ち、台帳件数からrecordを生成しない。
- PROHIBITED_BEHAVIOR: reported ledger countからobserved persistent truthを捏造。
- FAILURE_CLASS: `DESIGN_RESTORE_OBSERVED_VS_REPORTED_SYNC_VIOLATION`
- REFERENCE_FIXTURE: `PB-16,PB-25`
- INTRODUCED_REV: `rev0.313`
- SUPERSEDES: `NARROW_DELTA_ONLY_NO_HISTORICAL_DELETION`
- CONFLICT_PRECEDENCE: 現turnの父明示scope > rev0.313 emergency/admin exception and outcome contract > inherited normal-turn gate; platform safety/authority remains higher.

### DESIGN.ARTIFACT.CLASS_CONTRACT_EVOLUTION
- RULE_ID: `DESIGN.ARTIFACT.CLASS_CONTRACT_EVOLUTION`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `PREPROCESS_AND_RESTORE`
- TARGET_COORDINATE: `CORE_WITH_FATHER_PRIVATE_ISOLATION`
- TRIGGER: 該当turnの前処理、再投入、受入又はcontinuity判定。
- REQUIREMENT: 旧session handoff fixtureをhistorical exampleとして維持し、manifest付きcurrent source classとfull GitHub package classを分離する。nearest physical fixtureは最新父指示と正本pipelineで解決する。
- PROHIBITED_BEHAVIOR: 旧2-TXT例の普遍化、full packageを3ファイルだけへ縮退。
- FAILURE_CLASS: `DESIGN_ARTIFACT_CLASS_CONTRACT_EVOLUTION_VIOLATION`
- REFERENCE_FIXTURE: `PB-20`
- INTRODUCED_REV: `rev0.313`
- SUPERSEDES: `NARROW_DELTA_ONLY_NO_HISTORICAL_DELETION`
- CONFLICT_PRECEDENCE: 現turnの父明示scope > rev0.313 emergency/admin exception and outcome contract > inherited normal-turn gate; platform safety/authority remains higher.


## rev0.314 最新directiveのowner別要求

### DESIGNDOC.REV314.AC_001
- RULE_ID: `DESIGNDOC.REV314.AC_001`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `REV0.314_CURRENT_PROFILE`
- SOURCE_REQUIREMENT_ID: `AC-001`
- SOURCE_CLASS: `DIRECTIVE_REQUIREMENT_NOT_FATHER_VERBATIM`
- REQUIREMENT: 上記項目を、会話ログの実際の SEQ 又は保持された証拠位置へ対応付けたトレーサビリティ表を添付せよ。未付番のドラフト参照は、最終ログの SEQ に置換又は併記せよ。
- SOURCE_TRACE: `admin/REV0.314_REQUIREMENT_TRACEABILITY.json` / AC-001
- PROHIBITED_BEHAVIOR: 本要求の出所・scope・未確認状態を消し、未実行の成功又は本人の逐語として昇格すること。
- CONFLICT_PRECEDENCE: `LATEST_EXPLICIT_FATHER_DIRECTIVE > REV314_CURRENT_PROFILE > RETAINED_OPTIONAL_PROFILE`

### DESIGNDOC.REV314.AC_002
- RULE_ID: `DESIGNDOC.REV314.AC_002`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `REV0.314_CURRENT_PROFILE`
- SOURCE_REQUIREMENT_ID: `AC-002`
- SOURCE_CLASS: `DIRECTIVE_REQUIREMENT_NOT_FATHER_VERBATIM`
- REQUIREMENT: 父の明示要求、実装案、事実の出所、未確認事項が識別できることを検証せよ。
- SOURCE_TRACE: `admin/REV0.314_REQUIREMENT_TRACEABILITY.json` / AC-002
- PROHIBITED_BEHAVIOR: 本要求の出所・scope・未確認状態を消し、未実行の成功又は本人の逐語として昇格すること。
- CONFLICT_PRECEDENCE: `LATEST_EXPLICIT_FATHER_DIRECTIVE > REV314_CURRENT_PROFILE > RETAINED_OPTIONAL_PROFILE`

### DESIGNDOC.REV314.AC_003
- RULE_ID: `DESIGNDOC.REV314.AC_003`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `REV0.314_CURRENT_PROFILE`
- SOURCE_REQUIREMENT_ID: `AC-003`
- SOURCE_CLASS: `DIRECTIVE_REQUIREMENT_NOT_FATHER_VERBATIM`
- REQUIREMENT: 現行 rev0.313 / accepted baseline rev0.312、GitHub 作業保留、前処理再開、PR #1 未 merge という復元状態が互いに矛盾しないことを検証せよ。
- SOURCE_TRACE: `admin/REV0.314_REQUIREMENT_TRACEABILITY.json` / AC-003
- PROHIBITED_BEHAVIOR: 本要求の出所・scope・未確認状態を消し、未実行の成功又は本人の逐語として昇格すること。
- CONFLICT_PRECEDENCE: `LATEST_EXPLICIT_FATHER_DIRECTIVE > REV314_CURRENT_PROFILE > RETAINED_OPTIONAL_PROFILE`

### DESIGNDOC.REV314.AC_004
- RULE_ID: `DESIGNDOC.REV314.AC_004`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `REV0.314_CURRENT_PROFILE`
- SOURCE_REQUIREMENT_ID: `AC-004`
- SOURCE_CLASS: `DIRECTIVE_REQUIREMENT_NOT_FATHER_VERBATIM`
- REQUIREMENT: 既知の対応済み依頼を未対応へ戻す遷移、古い版への巻戻し、匿名投稿から本人経歴への混入、生成されていないコミット・検証・通知の成功宣言を拒否することを確認せよ。
- SOURCE_TRACE: `admin/REV0.314_REQUIREMENT_TRACEABILITY.json` / AC-004
- PROHIBITED_BEHAVIOR: 本要求の出所・scope・未確認状態を消し、未実行の成功又は本人の逐語として昇格すること。
- CONFLICT_PRECEDENCE: `LATEST_EXPLICIT_FATHER_DIRECTIVE > REV314_CURRENT_PROFILE > RETAINED_OPTIONAL_PROFILE`

### DESIGNDOC.REV314.AC_005
- RULE_ID: `DESIGNDOC.REV314.AC_005`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `REV0.314_CURRENT_PROFILE`
- SOURCE_REQUIREMENT_ID: `AC-005`
- SOURCE_CLASS: `DIRECTIVE_REQUIREMENT_NOT_FATHER_VERBATIM`
- REQUIREMENT: 無人の GitHub 変更又は新規リマインドを、このログ化命令の実行副作用として作成してはならない。
- SOURCE_TRACE: `admin/REV0.314_REQUIREMENT_TRACEABILITY.json` / AC-005
- PROHIBITED_BEHAVIOR: 本要求の出所・scope・未確認状態を消し、未実行の成功又は本人の逐語として昇格すること。
- CONFLICT_PRECEDENCE: `LATEST_EXPLICIT_FATHER_DIRECTIVE > REV314_CURRENT_PROFILE > RETAINED_OPTIONAL_PROFILE`

### DESIGNDOC.REV314.AC_006
- RULE_ID: `DESIGNDOC.REV314.AC_006`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `REV0.314_CURRENT_PROFILE`
- SOURCE_REQUIREMENT_ID: `AC-006`
- SOURCE_CLASS: `DIRECTIVE_REQUIREMENT_NOT_FATHER_VERBATIM`
- REQUIREMENT: 完了報告では成果物のリンク、逐語回収範囲、回収不能区間、検証結果及び次仕様への採用待ち状態を簡潔に示せ。
- SOURCE_TRACE: `admin/REV0.314_REQUIREMENT_TRACEABILITY.json` / AC-006
- PROHIBITED_BEHAVIOR: 本要求の出所・scope・未確認状態を消し、未実行の成功又は本人の逐語として昇格すること。
- CONFLICT_PRECEDENCE: `LATEST_EXPLICIT_FATHER_DIRECTIVE > REV314_CURRENT_PROFILE > RETAINED_OPTIONAL_PROFILE`

### DESIGNDOC.REV314.FORMAT_001
- RULE_ID: `DESIGNDOC.REV314.FORMAT_001`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `REV0.314_CURRENT_PROFILE`
- SOURCE_REQUIREMENT_ID: `FORMAT-001`
- SOURCE_CLASS: `DIRECTIVE_REQUIREMENT_NOT_FATHER_VERBATIM`
- REQUIREMENT: 現行root ZIP内の3-file source fixtureを物理検査済み。今回classは添付付き全タブログであり、fixture固有17 user又は旧2-root-TXTを固定件数・固定上限として流用するな。authority/current/FIXTURE_CLASS_INSPECTION.jsonを参照せよ。
- SOURCE_TRACE: `admin/REV0.314_REQUIREMENT_TRACEABILITY.json` / FORMAT-001
- PROHIBITED_BEHAVIOR: 本要求の出所・scope・未確認状態を消し、未実行の成功又は本人の逐語として昇格すること。
- CONFLICT_PRECEDENCE: `LATEST_EXPLICIT_FATHER_DIRECTIVE > REV314_CURRENT_PROFILE > RETAINED_OPTIONAL_PROFILE`

### DESIGNDOC.REV314.FORMAT_002
- RULE_ID: `DESIGNDOC.REV314.FORMAT_002`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `REV0.314_CURRENT_PROFILE`
- SOURCE_REQUIREMENT_ID: `FORMAT-002`
- SOURCE_CLASS: `DIRECTIVE_REQUIREMENT_NOT_FATHER_VERBATIM`
- REQUIREMENT: 原文を保持した五正本にはcurrent rev0.312 / baseline rev0.311 / detailed rev0.311の古いbuild snapshotが残る。父の最新指定current rev0.313 / baseline rev0.312 / detailed rev0.313を解釈上の現行値とし、原ファイルbytesは改変するな。
- SOURCE_TRACE: `admin/REV0.314_REQUIREMENT_TRACEABILITY.json` / FORMAT-002
- PROHIBITED_BEHAVIOR: 本要求の出所・scope・未確認状態を消し、未実行の成功又は本人の逐語として昇格すること。
- CONFLICT_PRECEDENCE: `LATEST_EXPLICIT_FATHER_DIRECTIVE > REV314_CURRENT_PROFILE > RETAINED_OPTIONAL_PROFILE`

### DESIGNDOC.REV314.FORMAT_003
- RULE_ID: `DESIGNDOC.REV314.FORMAT_003`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `REV0.314_CURRENT_PROFILE`
- SOURCE_REQUIREMENT_ID: `FORMAT-003`
- SOURCE_CLASS: `DIRECTIVE_REQUIREMENT_NOT_FATHER_VERBATIM`
- REQUIREMENT: 過去の同期PASSや件数は出所付きreported stateとして復元せよ。current receipt又はverified streakに昇格するな。
- SOURCE_TRACE: `admin/REV0.314_REQUIREMENT_TRACEABILITY.json` / FORMAT-003
- PROHIBITED_BEHAVIOR: 本要求の出所・scope・未確認状態を消し、未実行の成功又は本人の逐語として昇格すること。
- CONFLICT_PRECEDENCE: `LATEST_EXPLICIT_FATHER_DIRECTIVE > REV314_CURRENT_PROFILE > RETAINED_OPTIONAL_PROFILE`



## rev0.315 最新directiveのowner別要求

### DESIGNDOC.REV315.CORE_005
- RULE_ID: `DESIGNDOC.REV315.CORE_005`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `REV315_SHARED_CORE_AND_DISTRIBUTION`
- TARGET_COORDINATE: `ALL`
- TRIGGER: 最新ログの要求を次仕様へ統合し、会話・導入・配布・復元を評価するとき。
- REQUIREMENT: 共通coreを一つとし、利用者ごとの差を呼称・確認済み関係・許可された固有context・局所制約・私的状態へ限定する。共通応答品質を座標ごとに下げず、補助profileを第六正本や一般導入の必須添付にしない。
- PROHIBITED_BEHAVIOR: 座標間の私的状態混入、呼称による関係の認証、共通品質の引下げ。
- FAILURE_CLASS: `REV315_CORE_005_NONCONFORMANCE`
- SOURCE_CLASS: `DERIVED_REQUIREMENT_NOT_FATHER_VERBATIM`
- SOURCE_TRACE: `CORE-005` / T061, T063
- INTRODUCED_REV: `rev0.315`
- SUPERSEDES: `same-scope earlier assumptions only; historical source bytes remain immutable`
- CONFLICT_PRECEDENCE: 最新の明示的父指示 > 現行正本の権威境界 > REV315同scope候補条件 > 継承本文の旧build解釈

### DESIGNDOC.REV315.DIST_001
- RULE_ID: `DESIGNDOC.REV315.DIST_001`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `REV315_SHARED_CORE_AND_DISTRIBUTION`
- TARGET_COORDINATE: `ALL`
- TRIGGER: 最新ログの要求を次仕様へ統合し、会話・導入・配布・復元を評価するとき。
- REQUIREMENT: 一般導入の必須添付はprompt内の現行五正本5ファイルだけとする。共通設定・版指定はREADMEの自己完結した貼付文へまとめ、補助文書や公開restore JSONを必須添付に戻さない。アカウントの実制限と導入成功は別途検証する。
- PROHIBITED_BEHAVIOR: 七ファイル必須への逆戻り、未添付ファイルを貼付文の依存にすること。
- FAILURE_CLASS: `REV315_DIST_001_NONCONFORMANCE`
- SOURCE_CLASS: `DERIVED_REQUIREMENT_NOT_FATHER_VERBATIM`
- SOURCE_TRACE: `DIST-001` / T062, T063
- INTRODUCED_REV: `rev0.315`
- SUPERSEDES: `same-scope earlier assumptions only; historical source bytes remain immutable`
- CONFLICT_PRECEDENCE: 最新の明示的父指示 > 現行正本の権威境界 > REV315同scope候補条件 > 継承本文の旧build解釈

### DESIGNDOC.REV315.DIST_003
- RULE_ID: `DESIGNDOC.REV315.DIST_003`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `REV315_SHARED_CORE_AND_DISTRIBUTION`
- TARGET_COORDINATE: `ALL`
- TRIGGER: 最新ログの要求を次仕様へ統合し、会話・導入・配布・復元を評価するとき。
- REQUIREMENT: READMEは概要、版と正本、公開範囲、起動と共通設定、検証を先に置き、その後ろへインストールマニュアルを置く。五正本5添付と任意ユーザー名の確定済み手順を保つ。
- PROHIBITED_BEHAVIOR: マニュアル先頭版や特定利用者固定版への巻戻し。
- FAILURE_CLASS: `REV315_DIST_003_NONCONFORMANCE`
- SOURCE_CLASS: `DERIVED_REQUIREMENT_NOT_FATHER_VERBATIM`
- SOURCE_TRACE: `DIST-003` / T064
- INTRODUCED_REV: `rev0.315`
- SUPERSEDES: `same-scope earlier assumptions only; historical source bytes remain immutable`
- CONFLICT_PRECEDENCE: 最新の明示的父指示 > 現行正本の権威境界 > REV315同scope候補条件 > 継承本文の旧build解釈

### DESIGNDOC.REV315.PUB_002
- RULE_ID: `DESIGNDOC.REV315.PUB_002`
- OWNER: `DESIGNDOC`
- STATUS: `CANDIDATE_ACTIVE`
- SCOPE: `REV315_SHARED_CORE_AND_DISTRIBUTION`
- TARGET_COORDINATE: `ALL`
- TRIGGER: 最新ログの要求を次仕様へ統合し、会話・導入・配布・復元を評価するとき。
- REQUIREMENT: 受入済み現行正本と候補版を分け、歴史snapshotの五正本bytesを保持する。候補の作成でcurrent・baseline・詳細参照を昇格させない。履歴は直前2版とし、入れ子history・埋込archiveを作らず、manifest・CRC・再展開bytes一致を検証する。
- PROHIBITED_BEHAVIOR: 承認済み旧正本の上書き、候補の自動受入、再帰的履歴保持。
- FAILURE_CLASS: `REV315_PUB_002_NONCONFORMANCE`
- SOURCE_CLASS: `DERIVED_REQUIREMENT_NOT_FATHER_VERBATIM`
- SOURCE_TRACE: `PUB-002` / T011, T062, T063, T064
- INTRODUCED_REV: `rev0.315`
- SUPERSEDES: `same-scope earlier assumptions only; historical source bytes remain immutable`
- CONFLICT_PRECEDENCE: 最新の明示的父指示 > 現行正本の権威境界 > REV315同scope候補条件 > 継承本文の旧build解釈



## rev0.316 新規候補規則

