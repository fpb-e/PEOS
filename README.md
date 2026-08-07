# PEOS rev0.306-RC3

**状態:** `RELEASE_CANDIDATE / NOT_OPERATIVE / NOT_ACCEPTED / NOT_SELF_ACCEPTED / LIVE_HOST_ACCEPTANCE_PENDING`

## 位置づけ
- 現行operativeは`rev0.305`のまま。
- accepted baselineは`PEOS_GITHUB_PACKAGE_rev0.305.zip`、SHA-256 `69c99dd788f009726d20e43522822b288fa16eef03e7e4860fb34a4f23beae66`。
- rev0.306-RC1は`RETURNED_FOR_CORRECTION / AUDIT_ONLY`。
- rev0.306-RC2は未受入RCであり、RC3ではaudit/design referenceのみ。baseline・promotion sourceではない。
- RC3は親父の明示acceptanceまでoperativeへ昇格しない。

## RC3の主修正
「五正本を読んだ」ことと「runtimeがfirst user turn前にhostへbindされた」ことを分離した。
`RUNTIME.HOST.PRESESSION_BINDING_REQUIRED`と`RUNTIME.TIME.INGRESS_MICROKERNEL`をRUNTIME_GUARDが一意に所有する。

一般runtimeの必須入力は五正本だけであり、admin/validator/upper-canon tabへ通常稼働依存しない。
ただしstrict conformanceにはhostがpre-session bindingとpre-dispatch hookを実装し、actual traceを提供できる必要がある。

## 時刻ログ保持
session log / direct ledgerでは各user turnに以下を常設する。
`TURN_TIME_STATUS` / `USER_TURN_OBSERVED_AT_JST` / `TIME_EVIDENCE_CLASS` / `TIME_AUTHORITY`。
取得不能ならfieldを消さず、`UNAVAILABLE`または型付きnoncanonical evidenceを残す。

## 受入状態
- static package validation: build時に実validatorで判定
- fixture harness: static/liveとは別状態
- current build turn actual trace: 単発証跡
- `FIVE_CANON_COLD_START_LIVE_TRACE`: **PENDING**
- final release acceptance: **BLOCKED**
