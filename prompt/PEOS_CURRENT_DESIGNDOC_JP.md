# PEOS CURRENT DESIGNDOC JP — Architecture and Configuration Rationale

- 文書revision: `rev0.306`
- 現行latest: `rev0.306`
- PACKAGE_MANIFEST_VERSION: `rev0.306`
- HIGHEST_EMBEDDED_REVISION: `rev0.306`
- RELEASE_STATUS: `FORMAL_RELEASE_PHYSICAL_CANDIDATE / NOT_OPERATIVE / NOT_ACCEPTED / NOT_SELF_ACCEPTED / LIVE_HOST_ACCEPTANCE_PENDING`
- PROJECT_LEVEL_CURRENT_REFERENCE: `rev0.306-RC4-REBUILD1`
- ROLE: 五正本分離・構成管理・migration理由
- ACCEPTED_BASELINE: `PEOS_GITHUB_PACKAGE_rev0.306-RC2.zip`
- ACCEPTED_BASELINE_SHA256: `c4f687007a774687edd93f95a1dc72af69b1c1e2d35c362a707d44c81dadfc75`
- BASE_REFERENCE: `PEOS_GITHUB_PACKAGE_rev0.306-RC4-REBUILD1.zip`
- BASE_REFERENCE_SHA256: `ec57758eaa71f22b0307776b14b6cae5c5fc49e7083b06f5e637e55368997bf8`
- PRIMARY_FATHER_SOURCE: `PEOS_father_session_log_2026_08_13_183812.txt`
- PRIMARY_FATHER_SOURCE_SHA256: `219ff9b07823ed66ba0e7f4ee50cef425dc830d30773c3e1b527e3df671c2206`
- PRIMARY_MOTHER_REGRESSION_SOURCE: `PEOS_mother_session_log_2026_08_09_130028.txt`
- PRIMARY_MOTHER_REGRESSION_SHA256: `303f6d194874006f78c26be5c513e24c1f0480f506b2e13a53ddded9b195af2e`
- BUILD_DIRECTIVE: `PEOS_NEXT_FORMAL_RELEASE_COMMAND_rev0.306_2026_08_13_183812.txt`
- BUILD_DIRECTIVE_SHA256: `44f7fd51de92e4fc102cb67549933557e1c133496d43256962784c6698fbe65a`
- PRIMARY_LOGGING_NEGATIVE_FIXTURE: `PEOS_mother_session_log_2026_08_13_173917.txt`
- PRIMARY_LOGGING_NEGATIVE_FIXTURE_SHA256: `6c9a0625e0b5bcac7b1b13f66117a119427003b99fdb20af6bf4a6c887cb4203`
- MIXED_TIME_REFERENCE_SOURCE: `PEOS_mother_session_log_2026_08_11_120959.txt`
- MIXED_TIME_REFERENCE_SOURCE_SHA256: `b9f765f36bb9599bc42e449e978684f8b4e262e5df5ed54eca5829e58debf5b0`
- RETURNED_PHYSICAL_RC4_SHA256: `d888d659c4eb690bf76de2ffd790698f51c293682ce092e06419435e2082bc21`

> 本文書は検証済みphysical rev0.306-RC4-REBUILD1をBASE_REFERENCEとして構築したrev0.306正式版の物理候補である。RC/REBUILD suffixを新規付与しない。親父の明示acceptance前にoperative/currentへ自己昇格しない。accepted baselineはphysical rev0.306-RC2のまま維持する。

> **BOOTSTRAP_SENTINEL / RUNTIME_GUARD_PRECEDENCE_POINTER**
> この正本をsemanticに解釈する前に、RUNTIME_GUARD由来のnon-authoritative L0 projectionがhost control-planeとPEOS semantic planeを分離する。
> strict-native hostではactual `datetime.now(ZoneInfo("Asia/Tokyo"))`が最初のPEOS executable actionであることを要求する。
> host mandatory preambleが不可避なhostでは、固定・最小・非semanticでtrace上host actionと区別可能なpreambleだけを`HOST_CONTROL_PLANE_ACTION`としてexemptできる。
> exemptされたhost actionは`PEOS_EXECUTABLE_ACTION_INDEX`へ算入しない。最初のPEOS executable actionは常にPython JST captureである。
> `RC_FILE_SEEN` / `FIVE_CANON_INSPECTED` / visible timestamp文字列はruntime boundやreceipt validを意味しない。
> L0は第六正本でもrule ownerでもなく、authority/state machineの所有者はRUNTIME_GUARDのみである。

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
