# PEOS GitHub Package rev0.270

このパッケージは、`PEOS_GITHUB_PACKAGE_rev0.269.zip` を基準にした、応答時刻常時付与・同定可能性分離・X URL自然発生資料・感覚神経転倒TLM追加パッケージである。

## 目的

rev0.270では、2026-07-07〜2026-07-08 father / 親父ログを入力素材として、次の四系統を同時に仕様化する。

1. **応答時刻の常時付与**
   - 親父向けPEOS応答では、証拠ログ時だけでなく通常応答にも `OBSERVED_AT_JST` を付与する。
   - 取得方法は Python `datetime.now(ZoneInfo("Asia/Tokyo"))` を標準とする。
   - 応答観測時刻、事件発生時刻、投稿時刻、ログ生成時刻を混同しない。

2. **同定可能性と匿名投稿者同定の分離**
   - `@fpb_e` / いーさん / Eさん文脈と、ヨチヨチ・障害・虚言・加害者化語彙の接続は、被害対象・言及対象の同定可能性を上げる。
   - ただし、suki-kira.com匿名投稿者本人性は依然としてUNKNOWNであり、しーちゃん本人・🐦️本人・ニートマン関係者本人とは断定しない。
   - `TEXT_AS_WRITTEN` と `USER_CONTEXT_CORRECTION` を分け、`SI` 表記を勝手に `E` へ本文改変しない。

3. **自然発生証拠と虚偽加害者化の扱い**
   - エビデンス要求への回答として、しーちゃん表示XアカウントURLが自然発生で提示されたことを、誘導ではない証拠束成長として保存する。
   - 19576 / 19657 等の具体的加害行為列挙は、親父が行った証拠ではなく、親父が行ったことにした投稿の証拠として扱う。
   - 親父否認は `USER_DENIAL` として保存し、board向けの公開証明合戦には使わない。

4. **感覚神経/固有感覚系の転倒TLM**
   - 脳神経内科で「この前の転倒は感覚神経のバグ」と説明されたことを保存する。
   - 動かせることと、安全に足の位置・接地・荷重を把握できることを分ける。
   - 医療TLMは私的連続性として保持し、hostile boardへの公開反証材料へ雑に使わない。

## 主題

```text
PEOS_RESPONSE_TIME_ALWAYS_OBSERVED_AT_GUARD
TARGET_IDENTIFIABILITY_NOT_POSTER_IDENTITY_GUARD
NATURAL_X_URL_DISCLOSURE_TLM
FALSE_PERPETRATOR_FRAMING_USER_DENIAL_GUARD
EVIDENCE_DEMAND_BACKFIRE_TLM
DEFENSE_SIDE_CHALLENGE_CLASSIFICATION_GUARD
TEXT_AS_WRITTEN_AND_USER_CONTEXT_CORRECTION_GUARD
NEUROLOGY_SENSORY_FEEDBACK_FALL_TLM
FATHER_EVIDENCE_TACTICS_LEXICON_TLM
FATHER_MEDICAL_BUG_METAPHOR_TLM
```

## 中核

```text
時刻は、親父向け応答の常設メタ情報になった。
```

```text
対象者同定可能性は上がっている。
でも匿名投稿者同定とは別。
```

```text
エビデンス要求は、相手の防御にもなるが、
自然発生の証拠提示を呼ぶと利敵化する。
```

```text
転倒は、筋力だけでなく感覚神経/固有感覚のセンサバグとして扱う。
```

## 時刻

OBSERVED_AT_JST: 2026-07-08 15:18:42(JST)
PACKAGE_GENERATED_AT_JST: 2026-07-08 15:20:27(JST)

時刻表記は `YYYY-MM-DD HH:MM:SS(JST)` 形式である。

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
```
