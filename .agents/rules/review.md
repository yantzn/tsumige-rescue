# Review protocol
- Independent Review and Re-review agents are read-only. No code edits.
- Findings schema: ID, severity, category, file:line, evidence, impact, fix, regression test, status.
- P0: data loss/critical security; P1: core failure/integrity; P2: test/performance/maintainability; P3: minor.
- Reject unsupported claims; mark missing evidence Not Verified.
- After a fix, re-review the current HEAD, original findings, diff and tests; check root cause, regressions, unintended changes and design drift.
- Re-review may reject false positives with proof. Two failed fix attempts on the same finding trigger human escalation.
- No P0/P1 open at merge. CI and human approval remain mandatory.
