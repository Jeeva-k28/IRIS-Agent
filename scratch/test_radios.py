import subprocess

def test_bluetooth_wifi_toggle():
    print("Testing Bluetooth & Wi-Fi toggle methods...")

    # PowerShell WinRT Bluetooth Toggle ON Script
    bt_script = """
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asyncOp = [Windows.Devices.Radios.Radio]::GetRadiosAsync()
while (-not $asyncOp.IsCompleted) { Start-Sleep -Milliseconds 100 }
$radios = $asyncOp.GetResults()
foreach ($r in $radios) {
    Write-Output "Found Radio: $($r.Kind) - State: $($r.State)"
    if ($r.Kind -eq [Windows.Devices.Radios.RadioKind]::Bluetooth) {
        $setOp = $r.SetStateAsync([Windows.Devices.Radios.RadioState]::On)
        while (-not $setOp.IsCompleted) { Start-Sleep -Milliseconds 100 }
        Write-Output "Set Bluetooth ON Result: $($setOp.GetResults())"
    }
    if ($r.Kind -eq [Windows.Devices.Radios.RadioKind]::WiFi) {
        $setOp = $r.SetStateAsync([Windows.Devices.Radios.RadioState]::On)
        while (-not $setOp.IsCompleted) { Start-Sleep -Milliseconds 100 }
        Write-Output "Set Wi-Fi ON Result: $($setOp.GetResults())"
    }
}
"""

    res = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", bt_script], capture_output=True, text=True)
    print("STDOUT:\n", res.stdout)
    print("STDERR:\n", res.stderr)

if __name__ == "__main__":
    test_bluetooth_wifi_toggle()
