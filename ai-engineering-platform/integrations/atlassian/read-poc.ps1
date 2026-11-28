param(
    [string]$Twg = 'twg',
    [string]$IssueKey = 'TMGR-420',
    [string]$PageId = '16580612'
)

$ErrorActionPreference = 'Stop'
$site = 'https://yantzn.atlassian.net'

function Read-TwgJson([string[]]$Command) {
    $lines = & $Twg @Command --site $site -o json
    if ($LASTEXITCODE -ne 0) {
        throw "TWGの読み取りに失敗（終了コード $LASTEXITCODE）。要件確認を停止します。"
    }
    return ($lines -join [Environment]::NewLine) | ConvertFrom-Json
}

try {
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

    [pscustomobject]@{
        status = 'PASS'
        issueKey = $issue.key
        pageId = $page.id
        pageVersion = $page.snapshotToken
    } | ConvertTo-Json -Compress
} catch {
    [Console]::Error.WriteLine($_.Exception.Message)
    exit 1
}
