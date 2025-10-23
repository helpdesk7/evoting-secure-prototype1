# SR-11: Ballot Validation
- Enforce JSON Schema in `api/ballot/schema.json`.
- Server rules (next commits): known candidate IDs, no duplicates, contiguous ranks, max size, reject extra fields.
- Error responses: HTTP 400 with { "code": "<error>", "detail": "<message>" }.
