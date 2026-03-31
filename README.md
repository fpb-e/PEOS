# PEOS CURRENT CORE PACKAGE

このパッケージは、**擬似いーさんOS（PEOS: Pseud E-san Operating System）** の
**現行中核構成** をまとめた GitHub 向けパッケージである。

要するに、だ。
これは「完全版」ではない。
**今この時点での中核**であり、以後も更新され続ける前提の **CURRENT** である。

## 収録ファイル
- README.md
- CHANGELOG.md
- PEOS_CURRENT_SPEC_JP.md
- PEOS_CURRENT_LOG_ANTHOLOGY_JP.md
- PEOS_CURRENT_PAPER_JP.md
- PEOS_CURRENT_DESIGNDOC_JP.md

## 各ファイルの役割

### PEOS_CURRENT_SPEC_JP.md
現行統合仕様。PEOSの骨にあたる。

### PEOS_CURRENT_LOG_ANTHOLOGY_JP.md
現行ログ集。PEOSの肉にあたる。

### PEOS_CURRENT_PAPER_JP.md
構成部品として使う現行圧縮論文。PEOSの血流にあたる。

### PEOS_CURRENT_DESIGNDOC_JP.md
構成部品として使う現行設計書。
仕様書より一段抽象化した設計判断、三層構成、更新シーケンス、判断中核、危機対応、ログ運用、移植方針を圧縮保持する。

## 起動に取り込む対象
PEOS本体へ取り込む前提なのは、基本的に以下である。

- PEOS_CURRENT_SPEC_JP.md
- PEOS_CURRENT_LOG_ANTHOLOGY_JP.md
- PEOS_CURRENT_PAPER_JP.md
- PEOS_CURRENT_DESIGNDOC_JP.md

つまり、

- 仕様書 = 骨
- ログ集 = 肉
- 圧縮論文 = 血流
- 設計書 = 設計判断の圧縮保持

という形で運用する。

## 命名方針
- COMPLETE は使わない
- CURRENT を使う
- CURRENT は現行中核を意味し、完成を意味しない
- **完成は死** であり、CURRENT は生存状態の命名である

## 追加更新
- 構成部品として使う設計書を追加
- 長文の学術論文は別管理とする
