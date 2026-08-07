# PEOS CURRENT DESIGNDOC JP — Architecture and Configuration Rationale

- 文書revision: `rev0.306-RC3`
- 現行latest: `rev0.306-RC3`
- PACKAGE_MANIFEST_VERSION: `rev0.306-RC3`
- HIGHEST_EMBEDDED_REVISION: `rev0.306-RC3`
- RELEASE_STATUS: `RELEASE_CANDIDATE / NOT_OPERATIVE / NOT_ACCEPTED / NOT_SELF_ACCEPTED / LIVE_HOST_ACCEPTANCE_PENDING`
- OPERATIVE_CURRENT: `rev0.305`
- ROLE: 五正本分離・構成管理・migration理由
- SOURCE_BASELINE: `PEOS_GITHUB_PACKAGE_rev0.305.zip`
- SOURCE_BASELINE_SHA256: `69c99dd788f009726d20e43522822b288fa16eef03e7e4860fb34a4f23beae66`
- PRIMARY_DESIGN_SOURCE: `PEOS_father_session_log_2026_08_08_055037.txt`
- PRIMARY_DESIGN_SOURCE_SHA256: `cae1ae92a431c3b9bdb0df5f68d629fb57089129fad14e040471389e5171431b`

> このRC2はRC1差し戻し後の修正候補であり、live clean-session外部父レビュー完了前にoperativeへ昇格しない。

> **BOOTSTRAP_SENTINEL / RUNTIME_GUARD_PRECEDENCE_POINTER**
> 本文を解釈・適用する前に、`PEOS_CURRENT_RUNTIME_GUARD_JP.md` の
> `RUNTIME.HOST.PRESESSION_BINDING_REQUIRED` と `RUNTIME.TIME.INGRESS_MICROKERNEL`
> がhostへpre-session bind済みであることを要求する。
> `FIVE_CANON_AVAILABLE` / `FIVE_CANON_INSPECTED` は `RUNTIME_BOUND` を意味しない。
> state machineの所有者はRUNTIME_GUARDのみであり、本正本は重複実装しない。


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
- REQUIREMENT: rev0.305 ZIP、sidecar、manifest、evidenceをbyte不変で保持し、RCは別pathへ生成する。
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
- REQUIREMENT: baseline packageとmigration ledgerをhistory/provenance sourceとし、五正本本文へ再埋込しない。
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
