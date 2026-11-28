---
name: system-design
description: TMGRのsystem-design工程で使用する。
---

入力：確認済み要件、アーキテクチャ規約。
出力：docs/designs/TMGR-XX/配下の基本・詳細・データ・テスト設計Markdown。
責務境界、状態遷移、外部IF、失敗復旧、DB移行、テストケース、設計判断を記述する。
Confluenceへ投稿しない。独立設計レビュー前に実装へ進まない。設計書本文は日本語とする。

## 完了・失敗
根拠と対象SHAを記録する。必須入力や証跡が不足する場合は BLOCKED として統括へ返す。
