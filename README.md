# PEOS GitHub Package rev0.267

このパッケージは、`PEOS_GITHUB_PACKAGE_rev0.266.zip` を基準にした mother旅行・回復・特等席充電TLM 追加パッケージである。

## 目的

rev0.267では、2026-07-03〜2026-07-06の mother / お母さん旅行ログを、幸福旅行と身体負荷の二重保持として仕様化する。

主題は以下である。

```text
POST_VOMITING_RECOVERY_DUAL_HOLD_TLM
NIGHT_BUS_BIDIRECTIONAL_SLEEP_SUCCESS_TLM
SPECIAL_SEAT_RECHARGE_TRIP_COMPLETION_TLM
MEDICAL_WARNING_EXIT_AFTER_RECOVERY_EVIDENCE_GUARD
CONSIDERED_PURCHASED_CONSUMED_SEPARATION_GUARD
AWW_30L_OVERHEAD_SUCCESS_TLM
SALT_STACKING_MENU_PAIRING_TLM
MOCHAKO_ARM_PILLOW_COMPETITION_TLM
SEI_TRAVEL_COMPANION_TLM
```

## 中核

```text
幸福旅行は成立した。
身体負荷もあった。
どちらか片方で上書きしない。
```

```text
赤信号は落とさない。
でも、回復現物が出たら医療モードを畳む。
```

```text
味付き主食に濃い副菜を重ねると、塩気が渋滞する。
料理の失敗ではなく、編成問題。
```

## 時刻

USER_TURN_OBSERVED_AT_JST: 2026-07-06 07:12:08(JST)
PACKAGE_GENERATED_AT_JST: 2026-07-06 07:13:42(JST)

時刻表記は `YYYY-MM-DD HH:MM:SS(JST)` 形式である。

## 同梱ファイル

- `prompt/PEOS_CURRENT_SPEC_JP.md`
- `prompt/PEOS_CURRENT_RUNTIME_GUARD_JP.md`
- `prompt/PEOS_CURRENT_DESIGNDOC_JP.md`
- `prompt/PEOS_CURRENT_PAPER_JP.md`
- `prompt/PEOS_CURRENT_LOG_ANTHOLOGY_JP.md`
- `papers/PEOS_ACADEMIC_PAPER_JP.md`
- `README.md`
- `CHANGELOG.md`
- `PACKAGE_MANIFEST.txt`

## 正規化方針

```text
正規表記: rev0.xxx
順序: 昇順
言語: 日本語標準
```

## 注意

本パッケージは、rev0.264の `USER_TURN_OBSERVED_AT_JST`、rev0.266のregistered-user greeting一般化を維持する。新規主題はmother旅行・身体回復・生活TLMである。
