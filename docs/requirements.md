# Selected Security Requirements (Summary)

- R-06: Enforce TLS 1.3 (reverse proxy; HSTS; headers).
- SR-13: Session timeout & auto-logout (15 min access token; idle timer).
- SR-11: Strict ballot input validation (JSON Schema + server checks).
- SR-02: Secure voter address updates (authZ + immutable audit).
- SR-20: Secure results publication API (TLS + checksum/signature).

(Each has an Issue in GitHub with acceptance criteria and tests.)
