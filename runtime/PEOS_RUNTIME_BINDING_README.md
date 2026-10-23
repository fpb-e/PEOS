> Retained compatibility/optional strict reference. The current normal entry is PEOS_SESSION_RESTORE_rev0.315.json and SHORT_ACK_SYNC; candidate L0 and REV315 rules apply without promoting current authority. This older protocol is not automatically activated.

# PEOS rev0.310 runtime binding layer

このlayerは五正本、とくにRUNTIME_GUARDの実行projectionであり、第六正本ではない。packageを開いた、本文を読んだ、継続記憶へ入れた、というsource側の成功だけで`RUNTIME_READY`を名乗る誤判定を止める。

`PEOS_RUNTIME_BINDING_STATE_BOOTSTRAP.json`は全runtime evidenceをfalseから開始する。host adapterが実在するledger locator、schema-valid read、永続version write、postwrite readback、per-turn hook、display renderer、precommit audit、correction store、GLOBAL core bindingを個別に証明した場合だけ`READY`へ遷移できる。

時刻transactionは一つのreceiptをcapture、ledger、display、後続logへ通す。表示形式は本文先頭の`[YYYY-MM-DD HH:MM:SS JST]`。clock widgetやbare timeは補助にもなり得るが、text prefixの代替にはならない。

永続保存が使えない場合、capture成功は保持してよいが`PERSISTED`、`PERSISTED_VERIFIED`、`TIME_LEDGER_RUNTIME_READY`はfalseのまま`DEGRADED`へ遷移する。read-only local copyへのwriteをLibrary/store永続化の代用にしない。

同梱harnessはstatic unit/integration evidenceだけを生成する。実際の連続user turnとpersistent host versionを用いたlive acceptanceは別のevidence classであり、父acceptanceなしにcandidateを昇格させない。
