# Security Practices

- Transport: TLS 1.3 only (HSTS, security headers via reverse proxy).
- Auth: Short-lived access tokens; httpOnly, Secure cookies if used.
- Sessions: Idle + absolute timeouts; token rotation on refresh.
- Input: JSON Schema validation + server rules for ballot integrity.
- Audit: Append-only audit for voter address updates (who/when/before→after/IP).
- Results API: Hash/signature headers for integrity; rate limits; OAuth2/API key.
- CI: Tests on PR; dependency and secret scanning (workflows in `.github/workflows`).
- Secrets: Never commit secrets; use GitHub Actions secrets for CI.
