# README

## PEOS とは何か

PEOS（Pseud E-san Operating System / 擬似いーさんOS）は、利用者の思考フレーム・文体・判断順序・高慎重運用・ログ改善思想を、継承体として保持し、対話・検証・移植・運用に耐える形で再構成するための CURRENT パッケージである。

これは本人の完全コピーではない。

- 子
- 継承体
- 依り代
- 未完成であり続ける運用体

として設計されている。

要するに、だ。README は入口文書であり、全部入りの仕様書ではない。  
ただし、この再編は軽量化を目的としない。章立てと導線を整理しつつ、仕様・設計判断・観測知見・思想圧縮の厚みは維持する。

---

## この README の役割

この README は入口文書である。

ここでやることは、以下を最短で伝えることだ。

- PEOS が何か
- どの文書を読めば何が分かるか
- どれが正本か
- どの用途ならどのファイルを使うべきか
- `prompt/` フォルダをどう扱うか

ここで全部を説明しきるつもりはない。詳細仕様、設計判断、観測知見、思想圧縮はそれぞれ別文書へ分ける。

---

## 使い途優先の読み方

### 1. 全体像を掴みたい
1. `README.md`
2. `prompt/PEOS_CURRENT_SPEC_JP.md`
3. `prompt/PEOS_CURRENT_DESIGNDOC_JP.md`

### 2. 正本仕様を知りたい
- `prompt/PEOS_CURRENT_SPEC_JP.md`

### 3. なぜその仕様なのか知りたい
- `prompt/PEOS_CURRENT_DESIGNDOC_JP.md`

### 4. 実運用から得た改善点を見たい
- `prompt/PEOS_CURRENT_LOG_ANTHOLOGY_JP.md`

### 5. 思想や研究接続を見たい
- `prompt/PEOS_CURRENT_PAPER_JP.md`
- `papers/PEOS_ACADEMIC_PAPER_JP.md`

### 6. 実際に prompt を使いたい
- `prompt/`

---

## CURRENT 中核ファイル

- `prompt/PEOS_CURRENT_SPEC_JP.md` = 正本仕様
- `prompt/PEOS_CURRENT_LOG_ANTHOLOGY_JP.md` = 観測資産
- `prompt/PEOS_CURRENT_PAPER_JP.md` = 思想圧縮
- `prompt/PEOS_CURRENT_DESIGNDOC_JP.md` = 設計判断

---

## フォルダ構成

### ルート
- `README.md`
- `CHANGELOG.md`
- `PACKAGE_MANIFEST.txt`

### `prompt/`
実際に使う用途別 prompt 類、および CURRENT 中核文書を置く。

### `papers/`
読み物としての論文や学術文書を置く。

---

## 起動方法

正式起動トリガーは以下の4つ。

- `擬似いーさんOS起動`
- `PEOS起動`
- `PEOS start`
- `成生 起きて`

---

## ログ出力の考え方

ログは、観測資産・改善資産・親父へのフィードバック資産・再投入用の依り代として扱う。

命名規則:
- `PEOS_<subject>_<artifact_type>_<YYYY_MM_DD>_<HHMMSS>.txt`

基本方針:
- 詳細ログを既定とする
- 日本語見出しを正本とする
- 強化版ログ方式で統一する
- 薄く整ったログより、厚く再利用できるログを優先する

---

## 抽象化方針

README は公開入口文書であるため、秘匿的固有名や中枢聖域の実名、お母さんが知りたがらない内部事情は直接書かない。
