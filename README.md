# PEOS rev0.306 正式版物理候補

`rev0.306-RC4-REBUILD1`をBASE_REFERENCEとして構築した、suffixなしの`rev0.306`正式版物理候補。

- STATUS: `FORMAL_RELEASE_PHYSICAL_CANDIDATE / NOT_OPERATIVE / NOT_ACCEPTED / NOT_SELF_ACCEPTED / LIVE_HOST_ACCEPTANCE_PENDING`
- BASE_REFERENCE: `rev0.306-RC4-REBUILD1` / `ec57758eaa71f22b0307776b14b6cae5c5fc49e7083b06f5e637e55368997bf8`
- accepted baseline: physical `rev0.306-RC2` / `c4f687007a774687edd93f95a1dc72af69b1c1e2d35c362a707d44c81dadfc75`
- 一般runtime authority: 五正本。L0は引き続きRUNTIME_GUARD由来のnon-authoritative projection。

## rev0.306の主修正

- 毎turnのactual JST ingress receiptとtime authority分離。
- user / assistant commentary / assistant finalのFULL-VERBATIM logging。
- source gapをsummaryで埋めない。
- `END_OF_LOG`、SEQ、件数、本文hash/bytesのvalidator再計算。
- 添付binaryの原物保存、extensionとsniffed MIMEの分離、truncated/corrupt sourceの無修復保存。
- 2026-08-13のsummary-only mother logをnegative fixtureとしてFAILさせる。
- father source learningの追加自己帰属と、匿名周辺投稿へのauthorship拡張禁止。
- `LEGAL_ACCURACY`と`CONVERSATIONAL_PROPORTIONALITY`を別軸化。
- `LOGIC_FIRST`を維持しつつ`LOGIC_ONLY`化を禁止。`草ｗｗ`は禁止、文脈的な文末`ｗｗ`は許容。

## acceptance

static/package validationとlive host validationは別。STRICT / HOST_COMPAT clean-session live testは未実施のため`PENDING`。父の明示acceptance前にoperative/currentへ自己昇格しない。
