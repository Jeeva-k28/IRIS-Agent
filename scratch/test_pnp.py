import subprocess
import time

CREATE_NO_WINDOW = 0x08000000

def toggle_bt_pnp(enable: bool):
    print(f"Executing Bluetooth {'ON' if enable else 'OFF'}...")
    state_str = "$true" if enable else "$false"
    ps_cmd = f"""
$ErrorActionPreference = 'SilentlyContinue'

# 1. PnpDevice (Intel/Realtek/Broadcom/Qualcomm Bluetooth Adapter)
$bt = Get-PnpDevice -Class Bluetooth | Where-Object {{ $_.FriendlyName -match 'Intel|Realtek|Qualcomm|Broadcom|Adapter|Bluetooth' -and $_.FriendlyName -notmatch 'Enumerator|RFCOMM' }}
if ($bt) {{
    if ({state_str}) {{
        $bt | Enable-PnpDevice -Confirm:$false
    }} else {{
        $bt | Disable-PnpDevice -Confirm:$false
    }}
}}

# 2. NetAdapter
if ({state_str}) {{
    Enable-NetAdapter -Name *Bluetooth* -Confirm:$false
    Start-Service bthserv
}} else {{
    Disable-NetAdapter -Name *Bluetooth* -Confirm:$false
}}
"""
    res = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd], capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
    print("BT Pnp Output:", res.stdout, res.stderr)

def toggle_wifi_pnp(enable: bool):
    print(f"Executing Wi-Fi {'ON' if enable else 'OFF'}...")
    state_str = "$true" if enable else "$false"
    admin_state = "enabled" if enable else "disabled"
    ps_cmd = f"""
$ErrorActionPreference = 'SilentlyContinue'

# 1. NetAdapter
if ({state_str}) {{
    Enable-NetAdapter -Name *Wi-Fi*,*Wireless* -Confirm:$false
}} else {{
    Disable-NetAdapter -Name *Wi-Fi*,*Wireless* -Confirm:$false
}}

# 2. Netsh fallback
netsh interface set interface name="Wi-Fi" admin={admin_state}
"""
    res = subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_cmd], capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
    print("Wi-Fi Pnp Output:", res.stdout, res.stderr)

if __name__ == "__main__":
    t0 = time.time()
    toggle_bt_pnp(True)
    toggle_wifi_pnp(True)
    print(f"Completed in {time.time() - t0:.2f} seconds!")
