# CHANGELOG

## 更新内容
- ログ出力仕様にファイル命名規則を追加
- 命名規則は可読性優先とし、`PEOS_<subject>_session_log_<YYYY_MM_DD>_<HHMMSS>.txt` を採用
- 親父との対話ログは `subject = father` を使用
- 汎用名 `PEOS_session_log.txt` の使用を原則禁止
- session_id は原則としてファイル名に含めない
- README.md と CHANGELOG.md は既存名を維持
