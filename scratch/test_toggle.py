import subprocess

CREATE_NO_WINDOW = 0x08000000

def toggle_bt_sync(enable: bool):
    ps_cmd = f"""
$ErrorActionPreference = 'SilentlyContinue'

# 1. PnpDevice Enable/Disable
$bt = Get-PnpDevice -Class Bluetooth | Where-Object {{ $_.FriendlyName -match 'Intel|Realtek|Qualcomm|Broadcom|Adapter' }}
if ($bt) {{
    if ({'$true' if enable else '$false'}) {{
        $bt | Enable-PnpDevice -Confirm:$false
    }} else {{
        $bt | Disable-PnpDevice -Confirm:$false
    }}
}}

# 2. NetAdapter Enable/Disable
if ({'$true' if enable else '$false'}) {{
    Enable-NetAdapter -Name *Bluetooth* -Confirm:$false
}} else {{
    Disable-NetAdapter -Name *Bluetooth* -Confirm:$false
}}

# 3. Radio WinRT Sync GetAwaiter
try {{
    Add-Type -AssemblyName System.Runtime.WindowsRuntime
    $radios = [Windows.Devices.Radios.Radio]::GetRadiosAsync().GetAwaiter().GetResult()
    foreach ($r in $radios) {{
        if ($r.Kind -eq [Windows.Devices.Radios.RadioKind]::Bluetooth) {{
            $state = {'[Windows.Devices.Radios.RadioState]::On' if enable else '[Windows.Devices.Radios.RadioState]::Off'}
            $null = $r.SetStateAsync($state).GetAwaiter().GetResult()
        }}
    }}
}} catch {{}}
"""
    res = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd], capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
    print("BT Sync Result:", res.stdout, res.stderr)

def toggle_wifi_sync(enable: bool):
    ps_cmd = f"""
$ErrorActionPreference = 'SilentlyContinue'

# 1. NetAdapter Enable/Disable
if ({'$true' if enable else '$false'}) {{
    Enable-NetAdapter -Name *Wi-Fi*,*Wireless* -Confirm:$false
    netsh interface set interface name="Wi-Fi" admin=enabled
}} else {{
    Disable-NetAdapter -Name *Wi-Fi*,*Wireless* -Confirm:$false
    netsh interface set interface name="Wi-Fi" admin=disabled
}}

# 2. Radio WinRT Sync GetAwaiter
try {{
    Add-Type -AssemblyName System.Runtime.WindowsRuntime
    $radios = [Windows.Devices.Radios.Radio]::GetRadiosAsync().GetAwaiter().GetResult()
    foreach ($r in $radios) {{
        if ($r.Kind -eq [Windows.Devices.Radios.RadioKind]::WiFi) {{
            $state = {'[Windows.Devices.Radios.RadioState]::On' if enable else '[Windows.Devices.Radios.RadioState]::Off'}
            $null = $r.SetStateAsync($state).GetAwaiter().GetResult()
        }}
    }}
}} catch {{}}
"""
    res = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd], capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
    print("WiFi Sync Result:", res.stdout, res.stderr)

if __name__ == "__main__":
    print("Testing Sync Bluetooth & Wi-Fi toggling...")
    toggle_bt_sync(True)
    toggle_wifi_sync(True)
    print("Complete!")
