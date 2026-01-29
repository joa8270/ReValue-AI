$ports = @(8000, 4000)
foreach ($port in $ports) {
    try {
        $connections = Get-NetTCPConnection -LocalPort $port -ErrorAction Stop
        $pids_to_kill = $connections | Select-Object -ExpandProperty OwningProcess -Unique
        foreach ($p in $pids_to_kill) {
            if ($p -gt 0) {
                Write-Host "Killing process $p on port $port"
                Stop-Process -Id $p -Force -ErrorAction SilentlyContinue
            }
        }
    } catch {
        Write-Host "No process found on port $port"
    }
}
Write-Host "Starting MIRRA System..."
python run.py
