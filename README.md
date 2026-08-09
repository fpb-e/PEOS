# PEOS rev0.306-RC4

## 状態

- TARGET: `rev0.306-RC4`
- STATUS: `RELEASE_CANDIDATE / NOT_ACCEPTED / NOT_SELF_ACCEPTED / LIVE_HOST_ACCEPTANCE_PENDING`
- PROJECT_LEVEL_CURRENT_REFERENCE: `rev0.306-RC3`
- ACCEPTED_BASELINE: `PEOS_GITHUB_PACKAGE_rev0.306-RC2.zip`
- ACCEPTED_BASELINE_SHA256: `c4f687007a774687edd93f95a1dc72af69b1c1e2d35c362a707d44c81dadfc75`

RC4は親父の明示acceptance前にcurrent referenceへ昇格しません。

## 今回の主修正

RC3で残ったbootstrap chicken-and-eggを解消するため、full five-canon prebindをやめました。

pre-sessionでhostへbindするのは、RUNTIME_GUARDから生成された
`bootstrap/PEOS_L0_BOOT_SHIM.txt`だけです。

L0は**第六正本ではありません**。独立authorityでもありません。
役割は、semantic workを止めたまま各user turnの最初の実行として
`datetime.now(ZoneInfo("Asia/Tokyo"))`を実行し、actual receiptを検証することだけです。

receipt成功後に初めて五正本をload / validate / compileし、通常処理を許可します。

## 五正本

一般runtimeのsemantic canonは以下の五本です。

1. `prompt/PEOS_CURRENT_SPEC_JP.md`
2. `prompt/PEOS_CURRENT_RUNTIME_GUARD_JP.md`
3. `prompt/PEOS_CURRENT_DESIGNDOC_JP.md`
4. `prompt/PEOS_CURRENT_PAPER_JP.md`
5. `prompt/PEOS_CURRENT_LOG_ANTHOLOGY_JP.md`

L0、validator、manifest、evidence、registryは管理・host integration・受入試験用であり、semantic rule ownerではありません。

## father style learning

父direct sourceから、語彙だけでなく以下を構成管理します。

- usage condition
- rhythm
- sentence position
- humor timing
- correction habit
- argument structure
- when NOT to use a phrase
- evidence / OPSEC boundary

論戦styleのcoreはreactive/counterpunchです。
相手のexact wording、premise、evidence gap、contradiction、topic shiftを見てからtargeted counterを返します。
強い煽りやironyはsecondaryです。

assistant文、母発話、匿名投稿、第三者文、推定identityをfather vocabularyへ自動昇格しません。

## BOOT_CANON

logo/startup literalはoptional decorationではなくimmutable literalです。
欠落、whitespace normalization、文字置換、line rearrangement、extra fence metadata等は`BOOT_NONCONFORMANCE`です。

## live acceptance

static/package validatorやfixture harnessのPASSはlive host PASSではありません。
`tests/FIVE_CANON_COLD_START_LIVE_TRACE.json`が実clean-session multi-turn traceで埋まり、
親父が明示acceptanceするまではrelease acceptanceをBLOCKEDに維持します。

## delivery policy

session log、directive、evidence等の本文はchatへ全量出力しません。
deliveryはfilename、SHA-256、bytes、validation summary、linkを基本とします。
