# PEOS rev0.306-RC4-REBUILD1

## 状態

- TARGET: `rev0.306-RC4-REBUILD1`
- STATUS: `RELEASE_CANDIDATE / RETURN_CORRECTION_REBUILD / NOT_OPERATIVE / NOT_ACCEPTED / NOT_SELF_ACCEPTED / LIVE_HOST_ACCEPTANCE_PENDING`
- ACCEPTED_BASELINE: `PEOS_GITHUB_PACKAGE_rev0.306-RC2.zip`
- ACCEPTED_BASELINE_SHA256: `c4f687007a774687edd93f95a1dc72af69b1c1e2d35c362a707d44c81dadfc75`
- RETURNED_PHYSICAL_RC4_SHA256: `d888d659c4eb690bf76de2ffd790698f51c293682ce092e06419435e2082bc21`

差し戻し前physical RC4は上書きしていません。本rebuildも親父の明示acceptance前に自己受入・自己昇格しません。

## 主修正

旧RC4は「Python receipt前のcommentary/outputは0」という条件をhost mandatory preambleにも適用し、
platformが不可避にcontrol preambleを挿入する環境で永久fail-closedになりました。

本rebuildでは、起動前eventを
`HOST_CONTROL_PLANE_ACTION`と`PEOS_EXECUTABLE_ACTION`へ型分離し、
action indexも`HOST_ACTION_INDEX`と`PEOS_EXECUTABLE_ACTION_INDEX`へ分離します。

host mandatory preambleをexemptできるのは、RUNTIME_GUARDに列挙した10条件を全件actual traceで満たす場合だけです。
「commentaryなら何でもexempt」は禁止です。

verified host control eventの後でも、最初のPEOS executable actionは必ず
`datetime.now(ZoneInfo("Asia/Tokyo"))`です。

## conformance mode

- `STRICT_HOST_NATIVE_MODE`
- `HOST_COMPAT_BOOTSTRAP_MODE`

compat PASSをstrict PASSとは表示しません。strict hookがない場合も、compat pathを評価してから
`HOST_BOOTSTRAP_UNAVAILABLE`を判定します。

## 五正本とL0

semantic authorityは五正本だけにあります。
`bootstrap/PEOS_L0_BOOT_SHIM.txt`はRUNTIME_GUARDから生成するnon-authoritative projectionであり、第六正本ではありません。

## live acceptance

static/package validation、fixture harness、model self-audit、strict live trace、compat live traceは別evidence classです。
実clean-session live traceと親父の明示acceptance前は`RELEASE_ACCEPTANCE=BLOCKED`です。
