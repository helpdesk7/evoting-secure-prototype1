# R-06: Enforce TLS 1.3 and Security Headers

- All traffic forced HTTPS (301 redirect from HTTP).
- TLS 1.3 only (TLS 1.0–1.2 disabled).
- HSTS enabled with preload + includeSubDomains.
- Baseline security headers: HSTS, X-Content-Type-Options, Referrer-Policy, X-Frame-Options, CSP.

## Tests
- `curl -I http://host` → 301 to https
- `curl --tls-max 1.2 https://host` fails handshake
- Response headers visible in `curl -I https://host`
