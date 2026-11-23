# Implement TMGR feature — operator workflow
> This is a repository workflow specification. Confirm Antigravity workflow discovery and orchestration support in the installed version.

1. Requirements Agent: read Jira acceptance criteria and existing Confluence requirements; create a traceability table. Stop on conflicts.
2. Design Agent: write docs/designs/TMGR-XX/{basic-design,detailed-design,data-design,test-design}.md.
3. Design Review Agent (independent, read-only): verify traceability, architecture and failure modes. Block P0/P1.
4. Human gate for significant architectural or requirement changes.
5. Implement Agent: code and tests within agreed scope, updating design in the same branch.
6. QA Agent: execute checks and record evidence; unavailable tools => Not Run.
7. Review Agent (independent, read-only): findings with file/line evidence.
8. Fix Agent: resolve findings and add regression tests. Re-review Agent (independent): validate each resolution and side effects. Repeat at most twice per finding.
9. Security Review Agent: mandatory for photo/file, DB migration, backup/restore and billing, even with no other findings.
10. Orchestrator: verify mandatory CI, zero open P0/P1, design/code traceability, and prepare PR for human merge.
11. Never publish Markdown designs to Confluence.
