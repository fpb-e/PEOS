# 公開用ZIPのダウンロード

**[今回の仕様候補ZIPをダウンロード](PEOS_GITHUB_PACKAGE_next_spec_20261103.zip?raw=true)**

| 種別 | ファイル | サイズ |
|---|---|---|
| 次仕様候補・revision未採番 | [PEOS_GITHUB_PACKAGE_next_spec_20261103.zip](PEOS_GITHUB_PACKAGE_next_spec_20261103.zip?raw=true) | 611,704 bytes |
| 現行rev0.316の固定スナップショット | [PEOS_GITHUB_PACKAGE_rev0.316.zip](PEOS_GITHUB_PACKAGE_rev0.316.zip?raw=true) | 577,135 bytes |

今回の候補はPEOS_NEXT_SPEC_20261103です。現行rev0.316・accepted baseline rev0.315を維持し、候補の読解・試験・PRを新releaseの受入と扱いません。既存のrev0.316 ZIPは同一バイトで保持しています。

ZIPをそのまま添付して直下prompt/の五正本を読み込ませます。読めない環境では五正本5ファイルを個別添付します。いずれも同じ完全版設定を選べます。調査・要約のための添付と導入選択は区別します。詳しい指示は[インストールマニュアル](../README.md#インストールマニュアル)を参照してください。

リンク先がGitHubのファイル画面になった場合はDownload raw fileで保存できます。「Code → Download ZIP」はリポジトリ全体の取得です。

## チェックサムと保存方針

[SHA256SUMS](SHA256SUMS)と[公開パッケージ一覧](PUBLIC_PACKAGES.json)にファイル名・サイズ・SHA-256を記録しています。同名の配布物を後から差し替えません。

今回の候補SHA-256:

```text
df8f23ba933a272fe71b8f1e60ff9314bb47c55009f6a88f3b7a8d72f1a199d3
```

ZIP内部にはdownloads/、ZIP本体、配布用registry、および置き場だけを検査するrepository用試験を入れません。ZIP内のmanifestはその展開内容、リポジトリのmanifestは置き場も含む全体に対応します。五正本の内容は両者で一致します。今回の会話原文・画像・私的職務補足は公開ZIPへ入れません。
