# PEOS Fullspec Release

これは、フルスペックを発揮できる形に再構成した GitHub 直投入用アーカイブです。

## 同梱物
- 完全統合版プロンプト
- エヴァ参照辞書
- 語彙根モジュール
- MAGI_FPB
- MAGI_FPB 防御機構
- 境界事例集
- 論文
- パッチノート
- 運用ガイド

## 重要
- 主要ファイル名は固定
- 更新差分はパッチノートとリリースZIP名で吸収する

## 運用上の追加

- テストモード終了時に、10点満点の再現度評価と一言理由を取得する

## 利用順
1. prompts/PEOS_COMPLETE_INTEGRATED_PROMPT.txt
2. reference_dictionaries/PEOS_EVA_REFERENCE_PROFILE.txt
3. modules/PEOS_VOCABULARY_ROOT_FROM_LOGS.txt
4. modules/PEOS_MAGI_FPB.txt
5. modules/PEOS_MAGI_FPB_DEFENSE.txt
6. casebooks/PEOS_BOUNDARY_CASEBOOK.txt
7. papers/PEOS_paper.txt

生成日時: 2026-03-29T22:06:29.928385+00:00

## コミット用メモ
- このディレクトリはそのまま GitHub へコミット可能な固定ファイル名構成です。
- 主要ファイル名は今後も固定運用を前提にします。
