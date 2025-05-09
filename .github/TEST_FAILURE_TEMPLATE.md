---
title: ⚠️ Automated Test Failures Detected
labels: bug, needs-triage
assignees: ''
---

## Automated Test Failures

Tests are failing in the latest CI run!

### Workflow Run

Workflow: {{ env.GITHUB_WORKFLOW }}  
Run: [View details](https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }})  
Commit: ${{ github.sha }}

### What Failed

Please review the workflow logs to see which tests are failing.

### Next Steps

1. Check the error logs in the failed workflow run
2. Fix the tests or the code causing the failures
3. Re-run the workflow to verify your fixes

A maintainer should investigate this issue as soon as possible.