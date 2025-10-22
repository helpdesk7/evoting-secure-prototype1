# === eVoting Quick API Test Script ===
# Tests registration, token, ballot, and rate-limiting

Write-Host "`n=== Step 1: Check Eligibility ==="
$elig = Invoke-RestMethod -Method POST `
  -Uri http://localhost:8080/registration/eligibility/check `
  -Body (@{ voter_ref = "user123" } | ConvertTo-Json) `
  -ContentType "application/json"
$elig

Write-Host "`n=== Step 2: Get One-Time Token ==="
$tok = (Invoke-RestMethod -Method POST `
  -Uri http://localhost:8080/registration/ballot/token `
  -Body (@{ voter_ref = "user123"; minutes_valid = 5 } | ConvertTo-Json) `
  -ContentType "application/json").otbt
$tok

# === Step 3: Cast Ballot (send OTBT as header) ===
$headers = @{ "X-OTBT" = $tok }

$cast = Invoke-RestMethod -Method POST `
  -Uri http://localhost:8080/voting/ballot/submit `
  -Headers $headers `
  -Body (@{ prefs = @(1,2,3); election_id = "e2025" } | ConvertTo-Json) `
  -ContentType "application/json"

$cast | ConvertTo-Json


Write-Host "`n=== Step 4: Rate Limit Test ==="
for ($i=1; $i -le 40; $i++) {
  try {
    Invoke-RestMethod -Method POST `
      -Uri http://localhost:8080/registration/ballot/token `
      -Body (@{ voter_ref = "flood$i"; minutes_valid = 1 } | ConvertTo-Json) `
      -ContentType "application/json" | Out-Null
    "ok $i"
  } catch {
    "429 at $i"
    break
  }
}
