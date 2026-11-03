# 公開用ZIPのダウンロード

**[rev0.317をダウンロード](https://raw.githubusercontent.com/fpb-e/PEOS/3b4a21b98c0a787472898c2ecba31816ab195562/downloads/PEOS_GITHUB_PACKAGE_rev0.317.zip)**

| 版 | ファイル | サイズ |
|---|---|---|
| rev0.317 | [PEOS_GITHUB_PACKAGE_rev0.317.zip](https://raw.githubusercontent.com/fpb-e/PEOS/3b4a21b98c0a787472898c2ecba31816ab195562/downloads/PEOS_GITHUB_PACKAGE_rev0.317.zip) | 614,183 bytes |
| rev0.316（固定保存） | [PEOS_GITHUB_PACKAGE_rev0.316.zip](https://raw.githubusercontent.com/fpb-e/PEOS/f1e88672f877cf3f501b5ab34d0b66537f636f85/downloads/PEOS_GITHUB_PACKAGE_rev0.316.zip) | 577,135 bytes |
| 旧未採番build（固定保存） | [PEOS_GITHUB_PACKAGE_next_spec_20261103.zip](https://raw.githubusercontent.com/fpb-e/PEOS/f1e88672f877cf3f501b5ab34d0b66537f636f85/downloads/PEOS_GITHUB_PACKAGE_next_spec_20261103.zip) | 611,704 bytes |

今回の版はrev0.317です。完全版の機能設定を含む五正本を収録します。採番とrelease受入は別状態であり、現行権威の指定は所有者の上位正本に従います。

ZIPをそのまま添付し、直下prompt/の五正本を読み込ませます。ZIPを読めない環境では五正本を個別添付します。どちらも同じ完全版設定を選べます。[インストールマニュアル](../README.md#インストールマニュアル)を参照してください。

ダウンロードボタンは配布ZIPが実在するコミットに固定した絶対URLです。PRのマージやブランチ名に依存しません。

## チェックサム

[SHA256SUMS](SHA256SUMS)と[公開パッケージ一覧](PUBLIC_PACKAGES.json)に全配布物のファイル名・サイズ・SHA-256を記録しています。

rev0.317 SHA-256:

```text
98f544694fc8ebb94d5f290f2240020e9718cb4c05d5a6f8fbc586fed3cb9e58
```

既存ZIPは同一バイトで保存します。ZIP内部にはdownloads/や別のZIPを入れず、内部manifestはZIPの展開内容、リポジトリmanifestは配布用ファイルを含む全体に対応します。
