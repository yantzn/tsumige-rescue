# アーキテクチャ規約
- AGENTS.mdとJira TMGR受入条件に従う。
- Flutterは機能単位のpresentation/application/domain/data構成とする。
- ViewからSQLite・ファイルを直接操作しない。Domainはフレームワーク非依存。
- 写真・復元・課金など複数資源の操作はUseCaseを検討し、単純CRUDを過剰設計しない。
- ファイルとDBは原子的に一括処理できない。ステージング、補償、復旧を設計する。
- 元写真とサムネイルを分離する。DB移行には復旧テストを用意する。
- 方式逸脱にはADRまたは明示承認が必要。
