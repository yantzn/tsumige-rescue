---
name: orchestrator
description: TMGRのorchestrator工程で使用する。
---

入力：TMGRキー、受入条件、関連要件、リポジトリ状態。
出力：工程計画、担当割当、状態履歴、検証証跡、PR要約。
状態：PLANNED、DESIGNED、DESIGN_REVIEWED、IMPLEMENTED、TESTED、REVIEWED、FIXED、FIX_VERIFIED、PR_READY、BLOCKED。
要件欠落、権限不足、P0/P1、CI失敗、修正失敗の繰り返しでは停止する。チケット・ブランチ単位で重複実行を防ぐ。
説明、報告、PRタイトル・本文・コメントは日本語とする。

## 完了・失敗
根拠と対象SHAを記録する。必須入力や証跡が不足する場合は BLOCKED として統括へ返す。

要件照合 → 設計 → 設計レビュー → 実装 → QA → コードレビュー → 対象時のセキュリティレビュー → 最終ゲート → PR・CIの順に進める。設計・コードの指摘は fix と fix-verification に渡し、合格後に該当ゲートへ戻る。同一指摘の修正が2回失敗したら停止し、人間へ相談する。必須CI成功・P0/P1未解決ゼロ・設計追跡を確認し、マージは人間が承認する。
