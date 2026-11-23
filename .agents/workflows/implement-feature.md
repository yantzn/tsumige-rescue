# TMGR機能実装ワークフロー
この文書はリポジトリ上の実行手順。Antigravityによる自動認識・委譲は実環境で検証する。
1. Requirements Agent：Jira受入条件とConfluence要件を確認し追跡表を作る。矛盾時は停止。
2. Design Agent：docs/designs/TMGR-XX/に基本・詳細・データ・テスト設計Markdownを作成。
3. Design Review Agent：独立・読み取り専用で要件充足、方式、異常系を確認。P0/P1で停止。
4. 重大な方式・要件変更は人間承認を取得。
5. Implement Agent：承認済み設計に従い実装・テストを作り、設計書を同期更新。
6. QA Agent：テストを実行し証跡を残す。環境がなければ「未実行」。
7. Review Agent：独立・読み取り専用で根拠付き指摘を作成。
8. Fix Agent：指摘を修正し回帰テストを追加。Re-review Agentが独立検証。同一指摘の修正は最大2回。
9. Security Review Agent：写真・ファイル、DB移行、バックアップ・復元、課金では指摘の有無にかかわらず必須。
10. Orchestrator：CI成功、P0/P1未解決0、設計・コード追跡を確認してPRを準備。マージは人間承認。
11. 設計書をConfluenceへ自動投稿しない。PRのタイトル・本文・コメントは日本語とする。
