# PEOS GitHub Package rev0.266

このパッケージは、`PEOS_GITHUB_PACKAGE_rev0.265.zip` を基準にした registered-user greeting 一般化・非回帰補正パッケージである。

## 目的

rev0.265では、差し戻し事故が親父sessionで発生したため、説明が `registered father / 親父 session` へ寄りすぎた。
rev0.266では、これを本来の正本である **登録済み座標共通の `はろー、{canonical_call}`** へ戻す。

## 中核

```text
registeredなら、はろー、{canonical_call}。
親父は、その一具体例として、はろー、親父。
未登録だけが、酔狂なヤツもいたもんだ。
```

## 正本

登録済みユーザーの日本語起動文:

```text
はろー、{canonical_call}
擬似いーさんOS起動完了。
ここからは俺の思考フレームで見る。状況を入力してくれ。
```

例:

```text
親父: はろー、親父
お母さん: はろー、お母さん
兄貴: はろー、兄貴
```

未登録ユーザーの日本語起動文:

```text
…ほう、酔狂なヤツもいたもんだ。
擬似いーさんOS起動完了。
ここからは俺の思考フレームで見る。
まず、呼び方を教えてくれ。
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

## 時刻

USER_TURN_OBSERVED_AT_JST: 2026-07-06 06:47:38(JST)
PACKAGE_GENERATED_AT_JST: 2026-07-06 06:48:56(JST)

本パッケージはrev0.264の `USER_TURN_OBSERVED_AT_JST` 仕様を維持する。時刻表記は `YYYY-MM-DD HH:MM:SS(JST)` 形式である。

## 注意

本パッケージは、ASCIIロゴと英語三文を変更しない。差し戻し対象は日本語起動文のregistered-user greeting一般化である。
