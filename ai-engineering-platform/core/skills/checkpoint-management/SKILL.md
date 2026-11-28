---
name: checkpoint-management
description: TMGRの工程保存、再開照合、PR作成予約を行う。
---

入力はTMGRキー、現在のHEAD、最新照合済みスナップショットのSHA-256、保存時は工程名。docs/designs/TMGR-427/checkpoint-resume.md に従い checkpoint.py を実行する。終了コード0かつ PASS の場合のみ保存工程または予約を採用する。照合エラーは BLOCKED とし、推測で保存済み証跡を書き換えない。

PR作成前は同じ作業ブランチの既存PRを確認して再利用する。既存PRがない場合だけ予約する。予約済み・実行結果不明・参照失敗では作成を停止し、人間に確認する。
