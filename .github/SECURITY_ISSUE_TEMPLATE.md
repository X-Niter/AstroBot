---
title: 🚨 Critical Security Vulnerabilities Detected
labels: security, urgent, needs-triage
assignees: ''
---

## ⚠️ Security Alert: High Severity Vulnerabilities Detected

The automated security scan has detected one or more high severity security vulnerabilities in the codebase.

### Details

Workflow: {{ env.GITHUB_WORKFLOW }}  
Run: [View details](https://github.com/${{ github.repository }}/actions/runs/${{ github.run_id }})  
Commit: ${{ github.sha }}

### Potential Impact

High severity vulnerabilities can pose significant risks:
- Potential data breaches
- Unauthorized access to systems
- Service disruptions
- Other security implications

### Next Steps

1. Review the security reports in the workflow run
2. Prioritize fixing the high severity vulnerabilities
3. Consider temporarily disabling affected features if necessary
4. Re-run the security scan after applying fixes

Please address these vulnerabilities as soon as possible.