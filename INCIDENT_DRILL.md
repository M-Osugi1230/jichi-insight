# Incident response drill marker (2026-11-19)

This file exists only for the live incident-response drill recorded on
Issue #12 (2026-11-19). It has no effect on the site, data, or build.
It simulates a contaminated deployment so the P0 incident procedure in
docs/OPERATIONS_RUNBOOK.md section 6 can be exercised end to end:
detection via the publication status record, a merge freeze, rollback
by revert pull request, and recovery verification. It will be removed
by a revert pull request as part of the drill.
