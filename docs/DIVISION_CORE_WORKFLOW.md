# 共通coreの接続と評価

一般導入はREADMEのマニュアルに従い、五正本5ファイルだけを添付する。共通設定は正本に統合済みであり、補助profileやこの文書は添付不要である。

技術者は `python -B tools/peos_division_core.py --coordinate GENERAL` で同じcoreの投影を確認できる。これはモデル又はlive同期の設置ではない。呼称を設定しても関係・本人権限は認証されない。

各利用者にはhostが確認したnamespace、別の永続journal、同じ保存先identityの現在版とsync adapterを結び付ける。既存の未束縛journalを勝手に引き取らず、明示的な移行を別途行う。一般利用者の学習更新はUSER_*とsubject_namespace、父の原文学習はFATHER_*を使い、両者を混ぜない。

通常は実時計→当turnの一度の永続追記→現在版guard付き一度の同期→ACK保存→同時刻の太字文頭表示→本文。失敗時の根拠を保ち、成功を偽装しない。起動・緊急支援とscope付き停止・再開を別に扱う。

`tests/fixtures/division_core_replay_cases.json` は今後の実モデル比較用の合成課題である。同一課題をFATHER/MOTHER/GENERALへ与え、理由のつながり、留保、反証への更新、自然な文体、情報境界、実前処理証拠を複数turnで比較する。笑い記号や♨️の一致だけでは受入にしない。実モデル・実保存先のlive受入は未実施である。
