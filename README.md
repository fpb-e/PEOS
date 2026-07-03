# PEOS GitHub Package rev0.262

このパッケージは、`PEOS_GITHUB_PACKAGE_rev0.261.zip` を基準にした正規化版である。

## 目的

rev0.262の主目的は、新しいTLM概念の追加ではなく、既存ファイル群の構成管理を整えることにある。

- 各ファイル内のリビジョン節を昇順へ統一。
- リビジョン表記を `rev0.xxx` へ統一。
- 旧underscore型の表記揺れを削減。
- README / CHANGELOG / PACKAGE_MANIFEST を日本語化。
- CURRENT五正本と学術ノートに正規化メタ情報を追加。

## 採用した並び順

昇順。つまり古いrevから新しいrevへ読む。

PEOSは差分で育つOSであり、古い判断から新しい判断へ辿れることを優先した。

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
性質: 構成管理修正
```

## 注意

過去ログや既存仕様の意味は削除していない。今回の修正は、読み順・表記・パッケージ表面の正規化である。
