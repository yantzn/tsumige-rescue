param(
    [string]$Twg = 'twg',
    [string]$IssueKey = 'TMGR-420',
    [string]$PageId = '16580612',
    [ValidateSet('Read', 'Capture', 'Verify')]
    [string]$Mode = 'Read',
    [string]$SnapshotPath
)

$ErrorActionPreference = 'Stop'
[Console]::OutputEncoding = [System.Text.UTF8Encoding]::new($false)
$site = 'https://yantzn.atlassian.net'

function Read-TwgJson([string[]]$Command) {
    $lines = & $Twg @Command --site $site -o json
    if ($LASTEXITCODE -ne 0) {
        throw "TWGの読み取りに失敗（終了コード $LASTEXITCODE）。要件確認を停止します。"
    }
    return ($lines -join [Environment]::NewLine) | ConvertFrom-Json
}

function Get-Sha256([string]$Value) {
    $sha = [System.Security.Cryptography.SHA256]::Create()
    try {
        return [BitConverter]::ToString(
            $sha.ComputeHash([Text.Encoding]::UTF8.GetBytes($Value))
        ).Replace('-', '').ToLowerInvariant()
    } finally {
        $sha.Dispose()
    }
}

try {
    if ($Mode -ne 'Read' -and [string]::IsNullOrWhiteSpace($SnapshotPath)) {
        throw 'Capture/VerifyにはSnapshotPathが必要です。'
    }
    $jira = Read-TwgJson -Command @('jira', 'workitem', 'get', $IssueKey)
    $issue = @($jira.data)[0]
    if ($issue.key -ne $IssueKey -or -not $issue.description) {
        throw 'Jiraのキーまたは説明を確認できません。'
    }

    $confluence = Read-TwgJson -Command @(
        'confluence', 'content', 'get', $PageId, '--detail', 'full', '--format', 'md'
    )
    $page = $confluence.data
    if ($page.id -ne $PageId -or -not $page.snapshotToken -or
        -not ($page.body.value -or $page.body.outputFile)) {
        throw 'ConfluenceのページID、版、本文の参照を確認できません。'
    }

    if ($Mode -ne 'Read') {
        if (-not $issue.updated -or -not $page.body.value -or $page.body.lossyConversion) {
            throw 'Jiraの更新時刻または変換欠落のないConfluence本文を取得できません。'
        }
        $snapshot = [ordered]@{
            schemaVersion = 1
            site = $site
            issueKey = $issue.key
            issueVersion = [string]$issue.updated
            issueHash = Get-Sha256 (ConvertTo-Json -InputObject $issue.description -Depth 100 -Compress)
            pageId = $page.id
            pageVersion = $page.snapshotToken
            pageHash = Get-Sha256 $page.body.value
            retrievedAt = [DateTimeOffset]::UtcNow.ToString('o')
        }
        if ($Mode -eq 'Capture') {
            $path = $ExecutionContext.SessionState.Path.GetUnresolvedProviderPathFromPSPath($SnapshotPath)
            $json = ConvertTo-Json -InputObject $snapshot
            $stream = [IO.File]::Open($path, [IO.FileMode]::CreateNew)
            try {
                $bytes = [Text.Encoding]::UTF8.GetBytes($json)
                $stream.Write($bytes, 0, $bytes.Length)
            } finally {
                $stream.Dispose()
            }
        } else {
            $saved = Get-Content -LiteralPath $SnapshotPath -Raw -Encoding UTF8 | ConvertFrom-Json
            $retrieved = [DateTimeOffset]::MinValue
            if (-not [DateTimeOffset]::TryParse([string]$saved.retrievedAt, [ref]$retrieved)) {
                throw 'スナップショットの取得時刻が不正です。'
            }
            foreach ($field in $snapshot.Keys) {
                if ($field -ne 'retrievedAt' -and
                    ([string]$saved.$field -cne [string]$snapshot[$field])) {
                    throw "要件の最新版とスナップショットが一致しません（$field）。"
                }
            }
        }
    }

    [pscustomobject]@{
        status = 'PASS'
        mode = $Mode
        issueKey = $issue.key
        pageId = $page.id
        pageVersion = $page.snapshotToken
    } | ConvertTo-Json -Compress
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    if ($Mode -ne 'Read') {
        [pscustomobject]@{ status = 'BLOCKED'; mode = $Mode } | ConvertTo-Json -Compress
    }
    exit 1
}
