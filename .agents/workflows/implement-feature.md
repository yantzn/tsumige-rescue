# TMGR機能実装ワークフロー
> このファイルはリポジトリ上の実行手順定義である。Antigravityの自動検出・委譲機能は利用バージョンで確認する。

1. Requirements Agent：Jira受入条件と既存Confluence要件を取得し、追跡表を作る。矛盾があれば停止する。
2. Design Agent：docs/designs/TMGR-XX/ に基本・詳細・データ・テスト設計をMarkdownで作る。
3. Design Review Agent：独立・読み取り専用で要件充足、アーキテクチャ、異常系を確認する。P0/P1で停止する。
4. 重大な方式・要件変更は人間の承認を得る。
5. Implement Agent：承認設計に従ってコード・テストを作り、設計書を同期更新する。
6. QA Agent：テストを実行し証跡を残す。環境がなければ「未実行」とする。
7. Review Agent：独立・読み取り専用で根拠付き指摘を作成する。
8. Fix Agent：指摘を修正し回帰テストを追加する。Re-review Agentが独立検証する。同一指摘の修正は最大2回。
9. Security Review Agent：写真・ファイル、DB移行、バックアップ・復元、課金では指摘の有無にかかわらず必須。
10. Orchestrator：CI成功、P0/P1未解決0、設計・コード追跡、人間承認の条件を確認しPRを準備する。
11. Markdown設計書をConfluenceへ自動投稿しない。
