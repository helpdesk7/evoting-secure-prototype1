# SR-02: Address Update + Audit
- Endpoint: PUT /voters/{id}/address (self or admin scope `voter:write`)
- Concurrency: ETag on GET; If-Match required on PUT; 412 on mismatch
- Audit table (append-only): voterId, actorId, before, after, ip, userAgent, timestamp
- Fields validated; at-rest encryption for address fields (envelope key)
