# TMGR-420 TWG CLI読み取りPoC

認証済みのTWG CLIでJiraのチケット説明とConfluenceの要件本文を取得する。事前に対象サイトの読み取り権限を用意する。PowerShellからリポジトリルートで実行する。PATHにない場合は `-Twg` で実行ファイルを指定する。

```powershell
pwsh -NoProfile -File ai-engineering-platform/integrations/atlassian/read-poc.ps1
pwsh -NoProfile -File ai-engineering-platform/integrations/atlassian/read-poc.ps1 -IssueKey TMGR-999999
```

成功時はチケットキー・ページID・版をJSONで返す。TWGが失敗した場合や参照情報が不足する場合は終了コード1で停止する。Jiraの取得に失敗した場合はConfluenceの取得へ進まない。要件本文や認証情報はPoCの成功出力に含めない。

説明に受入条件が含まれることはJiraの実データで確認する。PoCは説明の有無を検証し、本文の意味や完全性までは判定しない。版付きスナップショットとPR前の最新照合はTMGR-419の後続範囲とする。
