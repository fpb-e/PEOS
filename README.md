# PEOS GitHub Package rev0.264

このパッケージは、`PEOS_GITHUB_PACKAGE_rev0.263.zip` を基準にした時刻取得仕様差分である。

## 目的

rev0.264の主目的は、ユーザー発話を受信した後にPythonでJST現在時刻を取得し、再投入可能ログへ絶対時刻アンカーとして保存する運用を定義することにある。

これはユーザー送信ボタン押下時刻そのものではない。衛星運用比喩では、CMD発行時刻ではなく、成生側で受信・処理されたTLM返却時刻に相当する。

## 中核

```text
CMD発行時刻ではなく、TLM返却時刻。
```

```text
送信瞬間の証明ではなく、ログの絶対時刻アンカー。
```

```text
Pythonが使えないなら捏造せず、ORDER_ONLY_STRICTへ降格する。
```

## 標準フィールド

```text
USER_TURN_OBSERVED_AT_JST
TIME_CAPTURE_METHOD: python datetime.now(ZoneInfo("Asia/Tokyo"))
TIME_CAPTURE_SEMANTICS: assistant-side turn observation / TLM返却時刻
```

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

rev0.264はrev0.262の正規化方針を維持する。リビジョン節は古いrevから新しいrevへ読む。

## 注意

本パッケージのログ標準時刻表記は `YYYY-MM-DD HH:MM:SS(JST)` である。

本パッケージは時刻取得運用仕様であり、UI/API上の送信時刻メタデータを取得したものではない。`USER_TURN_OBSERVED_AT_JST`は成生側観測時刻であり、ユーザー送信瞬間の法的秒単位証明ではない。
