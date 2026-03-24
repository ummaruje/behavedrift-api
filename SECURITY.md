# Security Policy

## Supported Versions

| Version | Security Fixes |
|---------|---------------|
| `1.x.x` (latest) | ✅ Actively supported |
| `< 1.0.0` (pre-release) | ❌ Not supported |

---

## Reporting a Vulnerability

**Do NOT report security vulnerabilities as public GitHub issues.** Public disclosure of a vulnerability before a fix is available puts users and their residents' data at risk.

### How to Report

Use **GitHub Private Security Advisories**:

1. Go to the [Security tab](https://github.com/umarisa/behavedrift-api/security) of this repository
2. Click **"Report a vulnerability"**
3. Complete the advisory form with as much detail as possible

Alternatively, email: **security@behavedrift.io**  
PGP key: Available on request via the email above.

### What to Include

Please provide as much of the following as possible:

- **Description** of the vulnerability
- **Steps to reproduce** (with curl commands, payloads, or proof-of-concept code)
- **Impact assessment** — what data or systems could be affected, and how
- **Affected versions**
- Your **preferred contact method** for follow-up

---

## Response Process

| Step | Timeframe |
|------|-----------|
| Acknowledgement of your report | Within 48 hours |
| Initial severity assessment | Within 5 business days |
| Fix developed and tested | Depends on severity (see below) |
| Release and public disclosure | After fix is released |

### Severity & Fix Timelines

| Severity | Definition | Target Fix Time |
|----------|-----------|----------------|
| **Critical** | Data exposure, auth bypass, RCE | 24–48 hours |
| **High** | Tenant isolation failure, privilege escalation | 7 days |
| **Medium** | Information disclosure, rate limit bypass | 30 days |
| **Low** | Minor information leakage, non-exploitable edge cases | 90 days |

---

## What We Consider In Scope

- Authentication and authorisation vulnerabilities
- Tenant data isolation failures (one tenant accessing another's data)
- Injection vulnerabilities (SQL, NoSQL, command)
- Insecure deserialization
- Sensitive data exposure (PII, pseudonymised resident data)
- GDPR-relevant data handling violations
- Server-Side Request Forgery (SSRF)
- Broken rate limiting enabling denial-of-service

## What We Consider Out of Scope

- Vulnerabilities in third-party dependencies (report to the upstream project; we will patch our dependency once a fix is released)
- Social engineering attacks targeting maintainers
- Physical security issues
- Denial of service via volumetric attacks (these are mitigated at infrastructure level)
- Scanner-generated reports with no proof of exploitability

---

## Responsible Disclosure Policy

We commit to:
- Respond to all reports in good faith
- Not pursue legal action against researchers who follow this policy
- Credit researchers in the release notes (unless anonymity is requested)
- Coordinate public disclosure timing with the reporter

We ask that you:
- Give us reasonable time to fix the issue before public disclosure
- Not access, modify, or delete data belonging to other users/tenants
- Not perform attacks that degrade service availability

---

## Data Classification

This API processes pseudonymised data relating to vulnerable adults. All vulnerability reports are treated with the highest priority. Resident data must never be used in proof-of-concept exploits — use the test tenant credentials provided in `.env.example` instead.

---

_Thank you for helping keep BehaveDrift and its users safe._
