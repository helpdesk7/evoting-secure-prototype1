# Security Requirements (My Assigned 5)

| Requirement ID | Description                                        | Priority | Complexity | Status     |
|----------------|----------------------------------------------------|----------|------------|------------|
| R-06           | Enforce TLS 1.3 with reverse proxy (Nginx/Caddy), disable legacy ciphers, HSTS + security headers | High     | Medium     | In Review  |
| SR-13          | Session timeout (15 min access token) & auto-logout with frontend idle timer, backend rejects expired tokens | High     | Medium     | In Review  |
| SR-11          | Strict ballot input validation using JSON Schema + server-side checks (valid candidate IDs, no duplicates, no rank holes) | High     | High       | Completed  |
| SR-02          | Secure voter address updates with authorization, ETag/If-Match, and immutable audit logging | High     | Medium     | Completed |
| SR-20          | Secure results publication API over TLS with OAuth2/API key and checksum header for integrity | Medium   | Medium     | Completed |


✅ SR-02: Address Audit API – Implemented and merged into main
✅ SR-11: Ballot Validation API – Implemented and merged into main
✅ SR-20: Results API – Implemented and merged into main
