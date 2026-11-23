# テスト規約
- 実装前に受入条件からテスト観点を導出する。
- 適用可能なUnit、Widget、統合テストを実行する。保存・写真・DB移行・復元には障害注入を追加する。
- Flutterが存在する場合：dart format --output=none --set-exit-if-changed .、flutter analyze --fatal-infos、flutter test、Androidビルド。
- 実行コマンド、結果、環境、コミットSHA、未実施理由を記録する。実行していないテストを成功と記載しない。
