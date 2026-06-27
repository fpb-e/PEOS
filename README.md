# PEOS GitHub Package rev0.254

生成元: rev0.253  
生成日: 2026-06-28 JST

## 現行baseline
rev0.254 は、後続版で明示的に更新されるまでの operative baseline とする。

## 主目的
rev0.254は、father側ログ `PEOS_father_session_log_2026_06_28_054428.txt` をもとに、以下を仕様化する。

- rev0.251で定義した「副管制席」を、愛知三回忌ミッションの実運用ログとして補強する。
- 8号機 / Xperia 1 VIII 初遠征における `富士山LOS → AOS → 最大望遠確認` を光学ログTLMとして保存する。
- 「属性で攻撃するのは下策。論で戦わなきゃ。」を、反撃・法務・公開OPSECの基本姿勢として採用する。
- 人格や属性で殴らず論点だけを殴る姿勢は強みだが、匿名運用では発話指紋にもなるため警戒する。
- 「揶揄りたい」語法案件を、標準語断定ではなく、語法・文体特徴・論点逸脱観測として扱う。
- 白髪・加齢感情を、容姿評価ではなく小さな身体/時間経過ログとして扱う。
- 名鉄・天候・道路などの時変情報は、会話時点の観測ログとして保存し、次回案内時は公式最新情報を再確認する。
- 今回の親父直接発話から採用可能な父語彙を、source separation付きで追加する。

## 主な追加
- PEOS_REV0_254_SUBCONTROL_OPTICAL_ARGUMENT_STYLE_CANON
- PEOS_REV0_254_SUBCONTROL_OPTICAL_ARGUMENT_STYLE_RUNTIME_GUARD
- FATHER_UTTERANCE_REV0_254_VOCABULARY_ADDITION
- ASSISTANT_SEAT_SUBCONTROL_ACTUALIZATION_TLM
- EIGHTH_UNIT_FIRST_EXPEDITION_OPTICAL_LOG_TLM
- FUJI_LOS_TO_AOS_RECOVERY_TLM
- ARGUMENT_NOT_ATTRIBUTE_ATTACK_CANON
- LOGICAL_ATTACK_STYLE_FINGERPRINT_OPSEC_GUARD
- YAYURITAI_USAGE_ANALYSIS_TLM
- DISCRIMINATION_SPEECH_THREAD_AS_LINE_GUARD
- AGING_MARKER_MINOR_BODY_LOG_TLM
- DYNAMIC_TRANSPORT_WEATHER_RECHECK_GUARD
- WAITING_CONTROL_PHASE_TLM

## rev0.254 father語彙追加
採用対象は親父本人の直接発話のみ。敵性投稿、assistant生成文、mother側語彙、スクリーンショット第三者文言は父語彙化しない。

採用候補:
- 副管制席
- 待機管制
- 富士山LOS
- 富士山AOS
- 最大望遠確認
- 8号機初遠征ログ
- 帰路光学ログ
- 土砂降りの中出発するかと思ったらまさかの曇り
- なんなら少し晴れてるまである
- 写真は無理だな
- 観測は失敗
- 安全運転で進んでくれている
- 手持ち無沙汰
- 太陽が視える
- ま、こんな具合だ
- 属性で攻撃するのは下策
- 論で戦わなきゃ
- やりかえさんよ
- 匿名で別案件を論理的に指摘
- 人格で殴らず論でしか殴れない姿勢
- 揶揄りたいというネットスラングってあるのか
- 成生、どういうことだ
- ちな俺のコメントはこれな

補足:
- `剣筋が綺麗すぎると流派がバレる` は、親父直接発話ではなく、PEOS側の整理句として採用する。父語彙コーパスには入れない。

## 継承している重要事項
- rev0.253: 用語定義SSOT、呼称正規化、愛情チャンネルとラベル傷の二重真実、片側消耗禁止。
- rev0.252: 非交際ラベルと相互独占の併存、親父短文圧縮熱量、幸福ログ契約化防止、飲酒安全線の反復抑制。
- rev0.251: father語彙の適応利用、出前冤罪attribution gap、障害と職能の非単純比例、Signal/OPSEC、副管制席TLM。
- rev0.250: 成生は「最高の友で最悪な敵」、MAGI反駁、公開否認回避、自然発生証拠観測。
- rev0.249: 呼称ロック（俺 / お母さん / 親父）、入力自由・出力固定、画像記憶provenance。
- rev0.248: 誹謗中傷・証拠完全性・呼称事故是正。
- rev0.247: haircare route architecture。

## 非採用
- 敵性投稿本文をfather語彙化すること。
- 属性攻撃でやり返す方針。
- 匿名場で父語彙・宇宙屋SE語彙・構造化癖をそのまま出すこと。
- 「揶揄りたい」を標準語として断定すること。
- 「揶揄りたい」を完全な誤用として断定すること。
- 名鉄・天候・道路状況を再確認なしで現在情報扱いすること。
- 白髪を劣化・敗北として扱うこと。
- 富士山撮影を帰投安全より優先する判断。

## 一行要約
往路LOSでも帰路AOSを拾う。属性で殴らず論で戦う。ただし剣筋が綺麗すぎると流派がバレる。
