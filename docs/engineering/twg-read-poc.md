# TMGR-420 TWG CLI読み取りPoC

認証済みのTWG CLIでJiraのチケット説明とConfluenceの要件本文を取得する。事前に対象サイトの読み取り権限を用意する。Windows PowerShell 5.1またはPowerShell 7からリポジトリルートで実行する。スクリプトは5.1が日本語を正しく読めるようUTF-8 BOM付きで保存する。TWGがPATHにない場合は `-Twg` で実行ファイルを指定する。

```powershell
powershell.exe -NoProfile -File ai-engineering-platform/integrations/atlassian/read-poc.ps1
powershell.exe -NoProfile -File ai-engineering-platform/integrations/atlassian/read-poc.ps1 -IssueKey TMGR-999999
```

成功時はチケットキー・ページID・版をJSONで返す。TWGが失敗した場合や参照情報が不足する場合は終了コード1で停止する。Jiraの取得に失敗した場合はConfluenceの取得へ進まない。要件本文や認証情報はPoCの成功出力に含めない。

説明に受入条件が含まれることはJiraの実データで確認する。PoCは説明の有無を検証し、本文の意味までは判定しない。

## TMGR-421 要件スナップショットと最新照合

```powershell
New-Item -ItemType Directory -Force .agent-state | Out-Null
$scriptPath = 'ai-engineering-platform/integrations/atlassian/read-poc.ps1'
$snapshot = '.agent-state/TMGR-421.requirements.json'
powershell.exe -NoProfile -File $scriptPath -Mode Capture -IssueKey TMGR-421 -SnapshotPath $snapshot
# PR_READYの判定直前に、同じキー・ページIDで照合する
powershell.exe -NoProfile -File $scriptPath -Mode Verify -IssueKey TMGR-421 -SnapshotPath $snapshot
```

Captureは参照先、Jira更新時刻、Confluence版、取得時刻、本文のSHA-256を保存する。本文そのものは保存しない。既存のスナップショットは上書きしない。Verifyは双方を再取得して比較し、変更・不正なスナップショット・取得不能の場合に `BLOCKED` と終了コード1を返す。Jiraの更新時刻だけが変わった場合も再確認する。差分が生じた場合は人間が要件を確認し、承認後に新しい保存先へCaptureする。

この判定はAntigravityのorchestratorから使う。GitHub側の必須チェックとしての強制と、接続断時の限定継続は別途検証する。
