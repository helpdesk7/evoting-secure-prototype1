# SR-20: Results API
- Endpoint: GET /results/latest (OAuth2 client-credentials or API key)
- Integrity: X-Checksum-SHA256 header (and optional signature)
- Caching: ETag/Last-Modified; support 304 via If-None-Match
- Rate limiting for abuse control
