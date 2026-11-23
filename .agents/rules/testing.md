# Test rules
- Define tests from acceptance criteria before implementation.
- Run relevant unit, widget and integration tests; use failure injection for storage, photos, migration and restore.
- On a Flutter-ready repo: dart format --output=none --set-exit-if-changed .; flutter analyze --fatal-infos; flutter test; Android build.
- Report exact command, outcome, environment, commit SHA and skipped checks. Never claim success without execution.
