import subprocess

def test_methods():
    print("Testing Bluetooth & Wi-Fi methods...")

    # Method 1: PnpDevice (Works on all Windows 10/11 machines natively for Bluetooth & Wi-Fi)
    ps_pnp = """
$bt = Get-PnpDevice -Class Bluetooth -ErrorAction SilentlyContinue | Where-Object { $_.FriendlyName -match 'Bluetooth|Adapter|Radio' }
if ($bt) {
    Write-Output "Found Bluetooth PnpDevice: $($bt.FriendlyName)"
}
$wifi = Get-NetAdapter -Name *Wi-Fi*,*Wireless* -ErrorAction SilentlyContinue
if ($wifi) {
    Write-Output "Found Wi-Fi NetAdapter: $($wifi.Name) - Status: $($wifi.Status)"
}
"""

    res = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_pnp], capture_output=True, text=True)
    print("STDOUT:\n", res.stdout)
    print("STDERR:\n", res.stderr)

if __name__ == "__main__":
    test_methods()
