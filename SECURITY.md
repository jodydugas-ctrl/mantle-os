# Security Policy

## Supported versions

Security fixes are provided for the latest release line.

| Version | Supported |
|---|---|
| 1.3.x | Yes |
| < 1.3 | Upgrade required |

## Reporting a vulnerability

Please use GitHub's private **Security advisories → Report a vulnerability** flow for this
repository. Do not publish credentials, resident identity keys, approval keys, raw prompts, or
proof-of-concept payloads in a public issue.

Include:

- the affected version and platform;
- the smallest reproducible sequence;
- expected and actual behavior;
- whether the issue crosses a Body, persistence, authority, host, or reproduction boundary; and
- any temporary mitigation you verified.

## Security boundaries

- Stage-1, Stage-2, containment, and `READY` are technical evidence, not production fusion
  authority.
- Production MIND fusion requires fresh resident-bound evidence plus distinct authenticated
  operator and guardian approvals.
- Reproduction is disabled by default and is not authorized by the 1.4.0 release.
- Authority credentials and provider credentials are deployment secrets and must never be
  committed.
- The Hermes addon is fail-open toward host operation but fail-closed toward fusion authority.

The project will acknowledge a complete private report when maintainers are available, assess
severity, and coordinate disclosure after a fix or mitigation exists. No fixed response-time SLA
is promised.
