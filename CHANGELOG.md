# CHANGELOG

## rev0.306-RC3
- immutable rev0.305 lineageから新規RCを構築。
- RC1は差し戻し/audit-only、RC2はaudit/design referenceのみ。
- five canon inspectionとpre-session runtime bindingを型分離。
- RUNTIME_GUARD先頭へINGRESS MICROKERNELを配置。
- 他四正本へBOOTSTRAP_SENTINELを追加し、rule ownershipはRUNTIME_GUARDへ一元化。
- actual receiptへturn/event/action/provider/value/trace/attempt/intervening-action bindingを要求。
- NO_LATE_REPAIRを維持。
- father/session logのper-turn時刻field常設とtyped time provenanceを追加。
- primary father sourceを`PEOS_father_session_log_2026_08_08_055037.txt`へ更新し、旧05:35ログをaudit-onlyへ降格。
- 草の使い方・文脈chain・OPSEC deltaをfather-direct fixtureへ追加。
- live clean-session multi-turn acceptanceは未実施のためPENDING。自動acceptしない。
