# TMGR-429 統括Skillの工程ルーティング

AGT-01・13・14・19・20のうち、Skillsの呼び出し順、合否の扱い、差し戻しを定義する。チケットを入力に orchestrator が統括し、工程ごとに context-management と checkpoint-management を適用する。

| 工程 | 呼び出し | 合格時 | 不合格・停止時 |
| --- | --- | --- | --- |
| 要件 | atlassian-integration → requirements-analysis | 設計 | 不明・取得不能は BLOCKED |
| 設計 | system-design → design-review | 実装 | 設計指摘は fix → fix-verification → 設計レビュー |
| 実装・QA | implementation → test-execution → quality-gate | コードレビュー | 実行済みの不合格は failure-analysis。修正可能なら実装へ。未実行・証跡不一致は BLOCKED |
| レビュー | code-review → 高リスク時は security-review | 最終判定 | 指摘は fix → fix-verification。PASS後に影響範囲のQAと該当レビューを再実行 |
| 修正検証 | 別コンテキストの読み取り専用 fix-verification | FIX_VERIFIED とし該当ゲートへ戻る | FAILは同じ指摘IDで差し戻す。2回目のFAILまたは判定不能は BLOCKED |
| 最終判定 | quality-gate → 要件の最新照合 → checkpoint-management | 必須条件がすべて合格なら PR_READY。既存PRを確認し、必要な場合だけ新規作成を予約 | 必須CI・要件・承認・証跡が欠ければ停止。手続き上取得できない場合は人間に相談 |

各工程で、参照した要件、現在のSHA、実施結果と次工程を記録する。試験では実行済みの設計・実装・レビューの入力を模擬し、通常経路、設計指摘、テスト不合格、修正検証FAILからの差し戻し、2回目FAIL、証跡の未実行・不一致を確認する。状態遷移と再試行上限をコードで強制する処理はTMGR-430で扱う。
