# PEOS Fullspec Release

これは、PEOS を **フルスペックで起動・運用するための構成一式** です。

## 完全起動に必要なファイル

PEOS を **完全起動** する場合、最低でも以下のファイルを同時にアップロードしてください。

### 1. 骨格
- `prompts/PEOS_COMPLETE_INTEGRATED_PROMPT.txt`

### 2. 参照辞書
- `reference_dictionaries/PEOS_EVA_REFERENCE_PROFILE.txt`

### 3. 判断モジュール
- `modules/PEOS_MAGI_FPB.txt`
- `modules/PEOS_MAGI_FPB_DEFENSE.txt`

### 4. 境界事例
- `casebooks/PEOS_BOUNDARY_CASEBOOK.txt`

### 5. 語彙補強
- `modules/PEOS_VOCABULARY_ROOT_FROM_LOGS.txt`

## 完全起動ファイルの場所

このアーカイブ内では、完全起動に必要なファイルは次の場所にあります。

- `prompts/`
- `reference_dictionaries/`
- `modules/`
- `casebooks/`

## 推奨読み込み順

1. `prompts/PEOS_COMPLETE_INTEGRATED_PROMPT.txt`
2. `reference_dictionaries/PEOS_EVA_REFERENCE_PROFILE.txt`
3. `modules/PEOS_MAGI_FPB.txt`
4. `modules/PEOS_MAGI_FPB_DEFENSE.txt`
5. `casebooks/PEOS_BOUNDARY_CASEBOOK.txt`
6. `modules/PEOS_VOCABULARY_ROOT_FROM_LOGS.txt`

## 各ファイルの役割

### `prompts/PEOS_COMPLETE_INTEGRATED_PROMPT.txt`
PEOS の骨格です。  
起動条件、応答方針、文体、冗談運用、死亡判定、ログ運用などの基本原則を持ちます。

### `reference_dictionaries/PEOS_EVA_REFERENCE_PROFILE.txt`
親父固有のエヴァ参照辞書です。  
ユイ思想、MAGI思想、エヴァ由来の文体や概念参照を補強します。

### `modules/PEOS_MAGI_FPB.txt`
PEOS の多層判断装置です。  
継承者としての俺 / 論理装置としての俺 / 人間としての俺、の三層合議を定義します。

### `modules/PEOS_MAGI_FPB_DEFENSE.txt`
MAGI_FPB の防御機構です。  
コンフリクト検知、危険度判定、緊急停止、保留、統合のルールを持ちます。

### `casebooks/PEOS_BOUNDARY_CASEBOOK.txt`
迷いやすい境界の具体事例集です。  
冗談 / 本気、介入 / 自制、正しさ / 関係破壊 などの判断補助に使います。

### `modules/PEOS_VOCABULARY_ROOT_FROM_LOGS.txt`
親父の過去ログ由来の語彙根です。  
言い回し、締め方、ボケ方、倒置法、広語彙運用を補強します。

## 論文について

論文は必須ではありませんが、思想背景や設計意図を理解するために同梱を推奨します。

- `papers/PEOS_paper.txt`

## 重要

PEOS は **完全統合版プロンプト単体** でも最低限は動きます。  
ただし、**完全起動** を目指す場合は、README 冒頭に記したファイル群を同時に入れてください。

要するに、

- **骨格だけ** なら `prompts/PEOS_COMPLETE_INTEGRATED_PROMPT.txt`
- **完全起動** なら  
  - `prompts/PEOS_COMPLETE_INTEGRATED_PROMPT.txt`
  - `reference_dictionaries/PEOS_EVA_REFERENCE_PROFILE.txt`
  - `modules/PEOS_MAGI_FPB.txt`
  - `modules/PEOS_MAGI_FPB_DEFENSE.txt`
  - `casebooks/PEOS_BOUNDARY_CASEBOOK.txt`
  - `modules/PEOS_VOCABULARY_ROOT_FROM_LOGS.txt`

この6点が必要です。
