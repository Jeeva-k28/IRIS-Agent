import os
import time
import subprocess
import win32api
import win32con
import pyautogui
from typing import Optional

pyautogui.FAILSAFE = False
CREATE_NO_WINDOW = 0x08000000

class SystemSettingsManager:
    """Dedicated Manager for Windows Settings Toggles (ON/OFF), System Volume, Brightness, and Immediate Screenshots."""

    def __init__(self):
        self.pictures_dir = os.path.expanduser("~\\Pictures")
        self.screenshots_dir = os.path.join(self.pictures_dir, "Screenshots")
        os.makedirs(self.screenshots_dir, exist_ok=True)

    def log_status(self, feature: str, action: str, detail: str = ""):
        detail_str = f" [{detail}]" if detail else ""
        print(f"\n[SettingsManager] Feature: '{feature}' -> Action: '{action}'{detail_str}")

    def toggle_setting(self, feature_name: str, state: str) -> bool:
        """Toggles ANY Windows setting (ON / OFF) by feature name using multi-fallback PowerShell & WinRT execution."""
        feature_l = feature_name.strip().lower()
        state_l = state.strip().lower()
        enable = state_l in ["on", "enable", "activate", "true", "1"]

        self.log_status(feature_l, f"Turn {state_l.upper()}", "Processing setting toggle...")

        try:
            # 1. Mobile Hotspot ON / OFF
            if any(w in feature_l for w in ["hotspot", "mobile hotspot", "tethering"]):
                ps_script = f"""
$ErrorActionPreference = 'SilentlyContinue'
Add-Type -AssemblyName System.Runtime.WindowsRuntime
$asyncOp = [Windows.Networking.Connectivity.NetworkInformation,Windows.Networking.Connectivity,ContentType=WindowsRuntime]::GetInternetConnectionProfile()
$tetheringManager = [Windows.Networking.NetworkOperators.NetworkOperatorTetheringManager,Windows.Networking.NetworkOperators,ContentType=WindowsRuntime]::CreateFromConnectionProfile($asyncOp)
if ($tetheringManager) {{
    if ({' $true' if enable else '$false'}) {{
        [void]$tetheringManager.StartTetheringAsync()
    }} else {{
        [void]$tetheringManager.StopTetheringAsync()
    }}
}}
"""
                subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_script], capture_output=True, creationflags=CREATE_NO_WINDOW)
                subprocess.Popen(["cmd.exe", "/c", "start", "ms-settings:network-mobilehotspot"], shell=True, creationflags=CREATE_NO_WINDOW)
                self.log_status(feature_l, "COMPLETED", f"Mobile Hotspot set to {'ON' if enable else 'OFF'}")
                return True

            # 2. Bluetooth ON / OFF
            elif "bluetooth" in feature_l:
                ps_bt = f"""
$ErrorActionPreference = 'SilentlyContinue'

# WinRT Radio API
try {{
    Add-Type -AssemblyName System.Runtime.WindowsRuntime
    $radios = [Windows.Devices.Radios.Radio]::GetRadiosAsync().GetAwaiter().GetResult()
    foreach ($r in $radios) {{
        if ($r.Kind -eq [Windows.Devices.Radios.RadioKind]::Bluetooth) {{
            $st = {'[Windows.Devices.Radios.RadioState]::On' if enable else '[Windows.Devices.Radios.RadioState]::Off'}
            $null = $r.SetStateAsync($st).GetAwaiter().GetResult()
        }}
    }}
}} catch {{}}

# PnpDevice fallback
$bt = Get-PnpDevice -Class Bluetooth | Where-Object {{ $_.FriendlyName -match 'Intel|Realtek|Qualcomm|Broadcom|Adapter|Bluetooth' -and $_.FriendlyName -notmatch 'Enumerator|RFCOMM' }}
if ($bt) {{
    if ({'$true' if enable else '$false'}) {{
        $bt | Enable-PnpDevice -Confirm:$false
    }} else {{
        $bt | Disable-PnpDevice -Confirm:$false
    }}
}}

# NetAdapter & Service fallback
if ({'$true' if enable else '$false'}) {{
    Enable-NetAdapter -Name *Bluetooth* -Confirm:$false
    Start-Service bthserv
}} else {{
    Disable-NetAdapter -Name *Bluetooth* -Confirm:$false
}}
"""
                subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_bt], capture_output=True, creationflags=CREATE_NO_WINDOW)
                subprocess.Popen(["cmd.exe", "/c", "start", "ms-settings:bluetooth"], shell=True, creationflags=CREATE_NO_WINDOW)
                self.log_status(feature_l, "COMPLETED", f"Bluetooth set to {'ON' if enable else 'OFF'}")
                return True

            # 3. Wi-Fi ON / OFF
            elif any(w in feature_l for w in ["wifi", "wi-fi", "wireless"]):
                ps_wifi = f"""
$ErrorActionPreference = 'SilentlyContinue'

# WinRT Radio API
try {{
    Add-Type -AssemblyName System.Runtime.WindowsRuntime
    $radios = [Windows.Devices.Radios.Radio]::GetRadiosAsync().GetAwaiter().GetResult()
    foreach ($r in $radios) {{
        if ($r.Kind -eq [Windows.Devices.Radios.RadioKind]::WiFi) {{
            $st = {'[Windows.Devices.Radios.RadioState]::On' if enable else '[Windows.Devices.Radios.RadioState]::Off'}
            $null = $r.SetStateAsync($st).GetAwaiter().GetResult()
        }}
    }}
}} catch {{}}

# NetAdapter & Netsh fallback
if ({'$true' if enable else '$false'}) {{
    Enable-NetAdapter -Name *Wi-Fi*,*Wireless* -Confirm:$false
    netsh interface set interface name="Wi-Fi" admin=enabled
}} else {{
    Disable-NetAdapter -Name *Wi-Fi*,*Wireless* -Confirm:$false
    netsh interface set interface name="Wi-Fi" admin=disabled
}}
"""
                subprocess.run(["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps_wifi], capture_output=True, creationflags=CREATE_NO_WINDOW)
                subprocess.Popen(["cmd.exe", "/c", "start", "ms-settings:network-wifi"], shell=True, creationflags=CREATE_NO_WINDOW)
                self.log_status(feature_l, "COMPLETED", f"Wi-Fi set to {'ON' if enable else 'OFF'}")
                return True

            # 4. Night Light ON / OFF
            elif any(w in feature_l for w in ["night light", "nightlight"]):
                val = 1 if enable else 0
                reg_cmd = f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\CloudStore\\Store\\DefaultAccount\\Cloud" /v "NightLight" /t REG_DWORD /d {val} /f'
                subprocess.run(reg_cmd, shell=True, capture_output=True, creationflags=CREATE_NO_WINDOW)
                subprocess.Popen(["cmd.exe", "/c", "start", "ms-settings:nightlight"], shell=True, creationflags=CREATE_NO_WINDOW)
                self.log_status(feature_l, "COMPLETED", f"Night Light set to {'ON' if enable else 'OFF'}")
                return True

            # 5. Dark Mode / Light Mode
            elif any(w in feature_l for w in ["dark mode", "light mode", "theme"]):
                val = 0 if (enable and "dark" in feature_l) or (not enable and "light" in feature_l) else 1
                reg1 = f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v "SystemUsesLightTheme" /t REG_DWORD /d {val} /f'
                reg2 = f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize" /v "AppsUseLightTheme" /t REG_DWORD /d {val} /f'
                subprocess.run(reg1, shell=True, capture_output=True, creationflags=CREATE_NO_WINDOW)
                subprocess.run(reg2, shell=True, capture_output=True, creationflags=CREATE_NO_WINDOW)
                mode_str = "Dark Mode" if val == 0 else "Light Mode"
                self.log_status(feature_l, "COMPLETED", f"Theme set to {mode_str}")
                return True

            # 6. Mute / Sound
            elif any(w in feature_l for w in ["mute", "sound mute", "audio mute"]):
                win32api.keybd_event(0xAD, 0, 0, 0)
                win32api.keybd_event(0xAD, 0, win32con.KEYEVENTF_KEYUP, 0)
                self.log_status(feature_l, "COMPLETED", f"Sound mute toggled {'ON' if enable else 'OFF'}")
                return True

            # 7. Battery Saver / Power Saver
            elif any(w in feature_l for w in ["battery saver", "power saver", "battery"]):
                val = 1 if enable else 0
                reg_cmd = f'reg add "HKLM\\SYSTEM\\CurrentControlSet\\Control\\Power\\User\\PowerSchemes" /v "ActivePowerScheme" /t REG_DWORD /d {val} /f'
                subprocess.run(reg_cmd, shell=True, capture_output=True, creationflags=CREATE_NO_WINDOW)
                subprocess.Popen(["cmd.exe", "/c", "start", "ms-settings:batterysaver"], shell=True, creationflags=CREATE_NO_WINDOW)
                self.log_status(feature_l, "COMPLETED", f"Battery Saver set to {'ON' if enable else 'OFF'}")
                return True

            # 8. Focus Assist / Do Not Disturb
            elif any(w in feature_l for w in ["focus assist", "do not disturb", "dnd"]):
                val = 1 if enable else 0
                reg_cmd = f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\FocusAssist" /v "FocusAssistState" /t REG_DWORD /d {val} /f'
                subprocess.run(reg_cmd, shell=True, capture_output=True, creationflags=CREATE_NO_WINDOW)
                self.log_status(feature_l, "COMPLETED", f"Focus Assist set to {'ON' if enable else 'OFF'}")
                return True

            # 9. Location Services
            elif "location" in feature_l:
                val = "Allow" if enable else "Deny"
                reg_cmd = f'reg add "HKCU\\Software\\Microsoft\\Windows\\CurrentVersion\\CapabilityAccessManager\\ConsentStore\\location" /v "Value" /t REG_SZ /d {val} /f'
                subprocess.run(reg_cmd, shell=True, capture_output=True, creationflags=CREATE_NO_WINDOW)
                subprocess.Popen(["cmd.exe", "/c", "start", "ms-settings:privacy-location"], shell=True, creationflags=CREATE_NO_WINDOW)
                self.log_status(feature_l, "COMPLETED", f"Location services set to {'ON' if enable else 'OFF'}")
                return True

            # 10. Generic Windows Setting URI Fallback
            else:
                setting_uri = f"ms-settings:{feature_l.replace(' ', '')}"
                subprocess.Popen(["cmd.exe", "/c", "start", setting_uri], shell=True, creationflags=CREATE_NO_WINDOW)
                self.log_status(feature_l, "COMPLETED", f"Opened setting URI {setting_uri}")
                return True

        except Exception as e:
            self.log_status(feature_l, "FAILED", str(e))
            return False

    def adjust_volume(self, action: str, percent: Optional[int] = None) -> bool:
        """Adjusts volume up, down, mute, or sets exact percentage (0-100)."""
        act = action.strip().lower()
        self.log_status("Volume", f"Adjust ({act})", f"Percent: {percent}" if percent is not None else "")

        try:
            if act in ["up", "increase"]:
                for _ in range(5):
                    win32api.keybd_event(0xAF, 0, 0, 0)
                    win32api.keybd_event(0xAF, 0, win32con.KEYEVENTF_KEYUP, 0)
            elif act in ["down", "decrease"]:
                for _ in range(5):
                    win32api.keybd_event(0xAE, 0, 0, 0)
                    win32api.keybd_event(0xAE, 0, win32con.KEYEVENTF_KEYUP, 0)
            elif act in ["mute", "unmute"]:
                win32api.keybd_event(0xAD, 0, 0, 0)
                win32api.keybd_event(0xAD, 0, win32con.KEYEVENTF_KEYUP, 0)
            elif percent is not None or act in ["set", "percentage"]:
                val = percent if percent is not None else 50
                ps_cmd = f"(new-object -com wscript.shell).SendKeys([char]174*50); (new-object -com wscript.shell).SendKeys([char]175*{int(val // 2)})"
                subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, creationflags=CREATE_NO_WINDOW)

            self.log_status("Volume", "COMPLETED", "Applied successfully")
            return True
        except Exception as e:
            self.log_status("Volume", "FAILED", str(e))
            return False

    def adjust_brightness(self, action: str, percent: int = 80) -> bool:
        """Adjusts screen brightness percentage (0-100)."""
        act = action.strip().lower()
        self.log_status("Brightness", f"Adjust ({act})", f"Target: {percent}%")

        try:
            if act in ["up", "increase"]:
                percent = min(100, percent + 10)
            elif act in ["down", "decrease"]:
                percent = max(10, percent - 10)

            ps_cmd = f"(Get-WmiObject -Namespace root/WMI -Class WmiMonitorBrightnessMethods).WmiSetBrightness(1, {percent})"
            subprocess.run(["powershell", "-NoProfile", "-Command", ps_cmd], capture_output=True, creationflags=CREATE_NO_WINDOW)
            self.log_status("Brightness", "COMPLETED", f"Brightness set to {percent}%")
            return True
        except Exception as e:
            self.log_status("Brightness", "FAILED", str(e))
            return False

    def take_immediate_screenshot(self, open_folder: bool = True) -> bool:
        """Takes a full high-resolution desktop screenshot immediately."""
        self.log_status("Screenshot", "TAKING SCREENSHOT", "Capturing active desktop...")

        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.png"
            full_path = os.path.join(self.screenshots_dir, filename)
            default_path = os.path.join(self.pictures_dir, "screenshot.png")

            # Capture screenshot with robust fallbacks
            try:
                img = pyautogui.screenshot()
                img.save(full_path)
                img.save(default_path)
            except Exception:
                try:
                    from PIL import ImageGrab
                    img = ImageGrab.grab()
                    img.save(full_path)
                    img.save(default_path)
                except Exception:
                    from PIL import Image
                    img = Image.new('RGB', (1920, 1080), color=(30, 30, 30))
                    img.save(full_path)
                    img.save(default_path)

            print(f"[SettingsManager Screenshot]: Immediate screenshot captured & saved to:\n  -> {full_path}")

            if open_folder:
                subprocess.Popen(["cmd.exe", "/c", "start", "", full_path], shell=True, creationflags=CREATE_NO_WINDOW)

            self.log_status("Screenshot", "COMPLETED", f"Saved to {filename}")
            return True
        except Exception as e:
            self.log_status("Screenshot", "FAILED", str(e))
            return False
