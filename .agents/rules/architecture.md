# アーキテクチャ規約
- AGENTS.mdとJira TMGRの受入条件に従う。
- Flutterは機能単位のpresentation/application/domain/data構成とする。
- ViewからSQLite・ファイルを直接操作しない。Domainはフレームワーク非依存。
- 写真・復元・課金など複数資源を扱う処理はUseCaseを検討する。単純CRUDは過剰設計しない。
- ファイルとDBは単一の原子トランザクションにならない。ステージング、補償、復旧を設計する。
- 元写真とサムネイルを分離し、DB移行の復旧テストを用意する。
- 方式逸脱はADRまたは明示承認を必要とする。
