# PEOS_REV0.317_20261103 規則競合の整理

既存443 IDを保持し、DESIGN.MODE.FULL_FEATURE_SELECTIONのみを追加、444 ID・一規則一所有者。

- 共通core・応答密度・薄い関係adapterへ品質不変を統合。
- PHILOSOPHY.MAGIが三者の意味、RUNTIME.MAGI.DELTA_ONLYが結論前の検討と表示の省略条件を所有。旧run_MAGI_only_if_delta_exists()の入口を置換。
- RUNTIME.TIME.USER_FACING_JST_DISPLAYと通常SHORT_ACK_SYNC契約を更新し、受領観測clockと前処理後display clockを分離。
- RUNTIME.FAIL.CLOSEDは無権限の作用を止め、単なる前処理不足で通常会話全体を止めない。低レベルtransactionの許可flagは会話の停止条件へ流用しない。
- ZIPと五正本個別添付は同じ導入設定を選択可能。旧物理5添付限定を更新。
- 変更した既存要求の旧traceは出所として保持し、current_binding_superseded_byで本候補の要求へ結ぶ。上書きは変更registryに列挙した規則だけ。
- 現行316・baseline315、対象revision未採番。旧build metadataとstrict監査の契約を現行の通常入口へ昇格しない。

静的整合性はvalidatorで検査する。実モデル品質・実接続・release受入は未実施。
