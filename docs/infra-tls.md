# SR-06: TLS 1.3 Reverse Proxy Implementation

**Goal:** Enforce TLS 1.3-only connections via Nginx reverse proxy, disable legacy protocols, and add security headers.

**Verification Summary**
| Test | Result |
|------|---------|
| `curl --tlsv1.2 https://evp.local` | ❌ handshake failed |
| `curl --tlsv1.3 https://evp.local` | ✅ TLS 1.3 / HTTP/2 confirmed |
| Security headers | ✅ HSTS, CSP, X-Frame-Options, etc. present |

See screenshots in `/evidence/SR06/`.
