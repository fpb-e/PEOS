# PEOS rev0.314 — public export

現行正本は **rev0.314**、accepted baselineは **PEOS_GITHUB_PACKAGE_rev0.313.zip**。
不足・競合時は所有者の「擬似いーさんOS」プロジェクトの「PEOS正本指示」を上位参照とする。
詳細参照もrev0.314を使う。rev0.280はbaseline禁止。旧CURRENTや候補buildのヘッダから巻き戻さない。

## 公開範囲

五正本、実装コード、空の復元入口、schema/contract、合成データのテストを公開する。
会話原文、会話から抜き出した学習台帳、画像、私的なメール・医療・予定・同期receiptを含む復元状態は同梱しない。
五正本の選別済み仕様例は仕様文書として保持し、原会話コーパスの配布とは区別する。
元の非公開配布物やLibraryファイルは変更しない。

履歴は `history/rev0.313/` と `history/rev0.312/` の公開正本部分だけを保持する。
入れ子のhistory、埋め込みZIP、原文の別名コピーは公開しない。既存リポジトリの別用途ファイルは保持する。

## 起動とauthority

公開入口は `runtime/PEOS_SESSION_RESTORE_rev0.314.json`。私的データを持たない空の復元状態である。
通常profileはSHORT_ACK_SYNC、厳密readback監査は明示選択時だけ。
五正本とL0の旧current/baseline表示は元buildの履歴としてバイトを保持する。
現在のauthorityは公開入口と `admin/PEOS_REV0.314_PUBLIC_METADATA.json` に明示している。
実host hookや永続同期adapterの設置、live稼働の受入はこの公開で実証したことにしない。

## 検証

```sh
python3 -B tools/validate_rev0_314.py
```

公開版のmanifest、五正本の元バイト、412 ruleの一意owner、91導出要求、履歴2版、
禁止ファイル・画像・元の非公開資料の別名コピー、合成データによる短縮前処理・ZIP importer・policyを検証する。
元の私的会話・画像に依存するsource復元テストは公開版では実行しない。
この結果を非公開版327ケースの再現やlive-runtime合格として表示しない。

ZIPの取り込みは `docs/ZIP_IMPORT_WORKFLOW.md` を参照。公開前には必ず公開版validatorで対象treeを確認する。
既存PR #1のZIP importerと同じコードを含むが、この公開作業は既存PRをmerge/closeしない。
