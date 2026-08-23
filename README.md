# PEOS rev0.307 RELEASE CANDIDATE — 2026-08-23

このpackageは現行project canon `rev0.306`を物理source referenceとして構築した**次仕様候補**である。

- BUILD_ID: `PEOS-REV0.307-CANDIDATE-20260823-211106-JST`
- TARGET_REVISION_LABEL: `rev0.307`
- CURRENT_PROJECT_CANON: `rev0.306`
- BASE_REFERENCE_SHA256: `f2eb04385feb06f8dc920472463f47c3fca1576554204813040d4753cb37b332`
- STATUS: `RELEASE_CANDIDATE / NOT_OPERATIVE / NOT_ACCEPTED / NOT_SELF_ACCEPTED`
- PRIMARY_SOURCE: `PEOS_father_session_log_2026_08_23_025032.txt`
- PRIMARY_SOURCE_SHA256: `cd352c85bdc18d686262a43420aa1eeee9e84d82c664d29536eb0ddd17c4dfe6`
- DIRECTIVE: `PEOS_NEXT_SPEC_BUILD_DIRECTIVE_2026_08_23_025032.txt`
- DIRECTIVE_SHA256: `d01a7b19efb2cc67e57f0bbf86054a2bf209c224818c9ef90e0d2dd40009fb89`

## 採番について

親父の2026-08-23指示により本候補のrevisionは`rev0.307`へ割り当て済み。acceptanceは別権限であり、親父の明示受入まではcurrent/operative `rev0.306`を変更しない。以後の仕様化では、明示overrideがない限り次の連番revisionを自動採番してよい。

## 主変更

1. `ログファイル化`を正式command化。
2. historical time欠落時の`USER_TURN_OBSERVED_AT_JST` placeholderを禁止しfield省略へ。
3. transcript本文をplain UTF-8化し、per-body SHA/bytes/hash-derived boundaryを禁止。file/attachment/bundle SHAは維持。
4. 父・母responseの秒精度JST常時表示契約。
5. father/non-father authority別log delivery。
6. evidence existence / anonymous identity / quote-speaker context guard。
7. dynamic domain freshness gate。
8. reminderをhost実automationに限定し、state separation・idempotency・privacy・no replayを正式化。
9. travel/medical/private continuityをDATA_ONLYとして保存し、reinjectionだけでside effectを起こさない。

## 検証クラス

- source bundle CRC/hash: machine verification
- session logger positive/negative: machine verification
- REMINDER-A～M: static mock-provider verification
- live multi-turn PEOS time guard: **PENDING**
- live host automation reminder: **PENDING**
- father external acceptance: **PENDING**

static passをlive passやacceptanceへ昇格しない。

## Revision numbering authority

2026-08-23、親父が本候補を`rev0.307`と指定し、今後は明示overrideがない限り次の連番revisionを自動インクリメントしてよいと許可した。revision割当はrelease acceptanceとは別であり、本candidateは明示受入まで`NOT_ACCEPTED`を維持する。
