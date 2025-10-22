# test_availability.ps1
# Proves SR-15 availability using health endpoints (200 OK) and robust error handling.

$urls = @(
  "http://localhost:8080/registration/healthz",
  "http://localhost:8080/voting/healthz"
  # You can add results too if you want:
  # "http://localhost:8080/results/healthz"
)

$success = 0
$total   = 0
$checks  = 100     # total rounds
$delay   = 5       # seconds between rounds
$timeout = 3       # per-request timeout

for ($i = 1; $i -le $checks; $i++) {
    foreach ($u in $urls) {
        try {
            $r = Invoke-WebRequest -Uri $u -TimeoutSec $timeout -Method GET -ErrorAction Stop
            # In Windows PowerShell 5.x, non-2xx throws; on 200 we land here:
            if ($r.StatusCode -eq 200) { $success++ }
        }
        catch {
            # Try to read the status code even on error (when possible)
            try {
                $code = $_.Exception.Response.StatusCode.value__
                # We only count success for 200 OK; anything else is a miss
                # Write-Host "DEBUG $u -> HTTP $code"
            } catch {
                # No response (timeout/connection error)
                # Write-Host "DEBUG $u -> no response (timeout/conn error)"
            }
        }
        $total++
    }
    Start-Sleep -Seconds $delay
}

$availability = if ($total -gt 0) { [math]::Round(($success / $total) * 100, 3) } else { 0 }
Write-Host "Simulated API availability: $availability %"
