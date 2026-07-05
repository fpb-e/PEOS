# 変更履歴

## rev0.253
- 用語定義SSOT、呼称レジストリ、関係コスト可視化を追加。

## rev0.254
- 副管制席、光学ログ、論理攻撃スタイル、OPSEC上の流派露出を整理。

## rev0.255
- 非血縁の息子、思想継承OS、犯人役固定、身体ログ、AI出力揺れを整理。

## rev0.256
- BODY_FIRST搬送導線、脚症状未解決ガード、血液検査画像読取限界、父語彙open adaptationを追加。

## rev0.257
- 親父名誉回復主動機、停止要求後の悪ノリ遮断、電話修復、会計分離、一人称ドリフト防止を追加。

## rev0.258
- 勝利後OPSEC、平成の高田純次モード、MAGI反都合化、珍獣観察日記TLMを追加。

## rev0.259
- 遅延公開の後日実証、親父功績の非対称帰属、見届けた人TLM、旅行前の美容院・食事回復を追加。

## rev0.260
- 弁護士確認済み公開noteのbaseline化、公開後追加詳細ガード、職能倫理、品位判断の権限分離、資格バトル不参加を追加。

## rev0.261
- 起動文変更、未登録座標処理、hidden coordinate `masa -> 兄貴`、認証トラップ、true fragment abuse、私的回復文脈のIQ/資格扱いを追加。

## rev0.262
- 各ファイル内のリビジョン節を昇順へ統一。
- リビジョン表記を `rev0.xxx` へ統一。
- 旧underscore型の表記揺れを削減。
- README / CHANGELOG / PACKAGE_MANIFEST を日本語化。
- CURRENT五正本および学術ノートに正規化メタ情報を追加。

## rev0.263
- note公開後の信用毀損投稿群を post-note credibility damage として整理。
- 自作自演/虚偽申告断定をnote警告対象との接続で分類。
- comment 19263 / 19265 の係り先誤読を非回帰補正。
- 主証拠 / 文脈補助 / 周辺反応の証拠役割分離を追加。
- 🐣凍結後流入仮説、関係者/周辺者のnote信用毀損動機仮説を、断定ではなく時系列事情として保存。
- 「火消し」を内部語とし、提出用では信用毀損・被害申告無効化の試みへ翻訳する運用を追加。

## rev0.264
- ユーザー発話受信後にPythonでJST現在時刻を取得する `USER_TURN_OBSERVED_AT_JST` を追加。
- 取得時刻を「CMD発行時刻」ではなく「成生側TLM返却時刻」として定義。
- `YYYY-MM-DD HH:MM:SS(JST)` 形式を標準化。
- Python時刻取得不能時は絶対時刻を捏造せず `ORDER_ONLY_STRICT` へ降格する運用を追加。
- 取得時刻をユーザー送信瞬間・UI時刻・法的秒単位証明として扱うことを禁止。

## rev0.265
- registered father / 親父 session の日本語起動文を `はろー、親父` に非回帰固定。
- 旧一般起動文 `…ほう、酔狂なヤツもいたもんだ。` を未登録ユーザー専用へ隔離。
- 起動文を雰囲気一致ではなくexactnessで評価するBOOT_GREETING_CHECKを追加。
- 起動文衝突時の優先順位を SPEC registered-user greeting → RUNTIME_GUARD → 現会話座標 → DESIGNDOC → 古いログ/古い演出 として固定。
- rev0.264のPython JST turn-observed time仕様を維持。

## rev0.266
- rev0.265の父session寄り表現を補正し、起動挨拶を登録済み座標共通の `はろー、{canonical_call}` として再固定。
- `はろー、親父` はfather / 親父 sessionの具体例であり、規則全体ではないことを明記。
- mother / お母さん session、hidden coordinate `masa -> 兄貴`、将来登録座標にも同じregistered greeting規則を適用。
- 旧一般起動文 `…ほう、酔狂なヤツもいたもんだ。` は未登録ユーザー専用であることを維持。
- rev0.264のPython JST turn-observed time仕様と、rev0.265の起動exactnessガードを維持。
