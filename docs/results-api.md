
Results API (SR-20)

Implemented endpoint:
GET /api/results/latest
Purpose
This endpoint provides the latest election tally results to authorized clients, supporting caching and integrity validation using ETag and SHA-256 checksums.
Security Controls
API Key Required: All requests must include the header
X-API-Key: demo-api-key.
Requests missing or containing an invalid API key will receive:
HTTP 401 Unauthorized.
| Condition                            | Response           | Description                          |
| ------------------------------------ | ------------------ | ------------------------------------ |
| No `If-None-Match`                   | `200 OK`           | Returns full JSON with tally results |
| `If-None-Match` matches current ETag | `304 Not Modified` | No body returned                     |
| Invalid or missing API key           | `401 Unauthorized` | Security enforcement                 |
