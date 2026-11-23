# 積みゲー救出隊 — AI Agent Rules

## Sources
- Jira TMGR: scope and acceptance criteria; Confluence: product requirements.
- GitHub Markdown in docs/: generated designs, ADRs, tests and engineering rules.
- Do not automatically publish generated designs to Confluence.
- Unknown or conflicting requirements: stop and report Not Verified.

## Execution
- Antigravity is the primary agent environment. Verify whether the installed version discovers .agents/ files before enabling autonomous workflows.
- Sequence: Requirements -> Design -> Design Review -> Implement -> QA -> Review -> Fix (when findings exist) -> Re-review -> PR.
- Reviewers are read-only and independent of implementers. Human approval is required for merge.
- Every change must trace to a TMGR issue. Keep designs and code synchronized in the same PR.

## Architecture
- Flutter, Android first, iOS later, offline/local-first.
- Feature-first MVVM with Riverpod and repository abstractions; Drift/SQLite remain subject to PoC and ADR.
- Presentation must not directly manipulate SQL/files; domain must not depend on Flutter/Drift.
- Preserve existing game records and original photos on failures.

## Review gates
- Findings require ID, severity P0-P3, file/line, evidence, impact, fix, regression test and status.
- Unresolved P0/P1 block merge. Mandatory CI must pass.
- After each fix, independent Re-review validates root cause, regressions and side effects.
- Stop and escalate after two failed fixes of the same finding.

## Security
- Never transmit credentials, tokens, real user photos, private records or sensitive logs to AI tools.
- Require Security Review for photos, DB migrations, backup/restore and billing.
- Validate paths, file formats, size limits, archive traversal and decompression limits. Avoid custom cryptography.

## Verification
- When Flutter exists: dart format --output=none --set-exit-if-changed ., flutter analyze --fatal-infos, flutter test, Android build.
- Record Not Run / Not Verified if environment or evidence is unavailable; never claim unexecuted tests passed.
