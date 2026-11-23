# Security constraints
- Do not read or transmit secrets, tokens, private user data or production photos to AI tools.
- Never put secrets in source, prompts, logs, screenshots, tests or PR descriptions.
- Least-privilege integrations; do not publish, merge, delete user data, rotate keys or run destructive commands without human approval.
- Security review required for photo/file processing, DB migrations, backup/restore and billing.
- Check path traversal, ZIP Slip/Bomb, decompression limits, file signatures, oversized inputs, authentication of backups, interruption safety and dependency vulnerabilities.
- Use established authenticated encryption libraries; cryptographic choices require PoC and ADR.
