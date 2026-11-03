# 公開用ZIPのダウンロード

**[rev0.317をダウンロード](https://raw.githubusercontent.com/fpb-e/PEOS/80dd4a9812131013ccc5e34e9106ca0e40a5f03e/downloads/PEOS_GITHUB_PACKAGE_rev0.317.zip)**

| 版 | ファイル | サイズ |
|---|---|---|
| rev0.317 | [PEOS_GITHUB_PACKAGE_rev0.317.zip](https://raw.githubusercontent.com/fpb-e/PEOS/80dd4a9812131013ccc5e34e9106ca0e40a5f03e/downloads/PEOS_GITHUB_PACKAGE_rev0.317.zip) | 618,266 bytes |
| rev0.316（固定保存） | [PEOS_GITHUB_PACKAGE_rev0.316.zip](https://raw.githubusercontent.com/fpb-e/PEOS/f1e88672f877cf3f501b5ab34d0b66537f636f85/downloads/PEOS_GITHUB_PACKAGE_rev0.316.zip) | 577,135 bytes |
| 旧未採番build（固定保存） | [PEOS_GITHUB_PACKAGE_next_spec_20261103.zip](https://raw.githubusercontent.com/fpb-e/PEOS/f1e88672f877cf3f501b5ab34d0b66537f636f85/downloads/PEOS_GITHUB_PACKAGE_next_spec_20261103.zip) | 611,704 bytes |

rev0.317は所有者の明示指定により正式採用された現行正本です。accepted baselineはrev0.316、詳細参照はrev0.317。完全版の機能設定を含む五正本を収録します。

ZIPをそのまま添付し、直下prompt/の五正本を読み込ませます。ZIPを読めない環境では五正本を個別添付します。どちらも同じ完全版設定を選べます。[インストールマニュアル](../README.md#インストールマニュアル)を参照してください。

ダウンロードボタンは配布ZIPが実在するコミットに固定した絶対URLです。PRのマージやブランチ名に依存しません。

## チェックサム

[SHA256SUMS](SHA256SUMS)と[公開パッケージ一覧](PUBLIC_PACKAGES.json)に全配布物のファイル名・サイズ・SHA-256を記録しています。

rev0.317 SHA-256:

```text
cbdf55a6f6a95635b5869a3500231b65e7b2c431f3f51f85e8edb6d7147dc143
```

rev0.316と旧未採番ZIPは同一バイトで保存します。採用前rev0.317は既存の固定コミットで保存され、この案内は正式採用を反映したZIPを指します。ZIP内部にはdownloads/や別のZIPを入れず、内部manifestはZIPの展開内容、リポジトリmanifestは配布用ファイルを含む全体に対応します。
