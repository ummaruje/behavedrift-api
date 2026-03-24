---
name: Bug Report
about: Something is broken or behaving incorrectly
title: "[BUG] "
labels: bug, needs-triage
assignees: umarisa
---

## Bug Description
<!-- A clear and concise description of the bug. -->

## Steps to Reproduce

```bash
# Provide the exact curl command or code that reproduces the bug
curl -X POST https://your-instance/v1/observations \
  -H "Authorization: Bearer ..." \
  -d '{ ... }'
```

## Expected Behaviour
<!-- What did you expect to happen? -->

## Actual Behaviour
<!-- What actually happened? Include the full response body and status code. -->

**Response status code:** `4XX / 5XX`

**Response body:**
```json

```

## Environment

| Item | Value |
|------|-------|
| BehaveDrift version | `v1.x.x` |
| Deployment type | Docker / Source / Cloud |
| Python version | `3.x.x` |
| PostgreSQL version | `15.x` |
| OS | macOS / Linux / Windows |

## Logs
<!-- Include relevant log output. Redact any PII or secrets. -->

```
[paste logs here]
```

## Additional Context
<!-- Any other information that might be relevant. -->

---
**Note:** Do not include real resident data or API keys in bug reports. Use test data only.
