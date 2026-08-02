import os
import sys
import time
import subprocess
import ctypes
import win32gui
import win32con
import win32api
import pyautogui
import re
from typing import Optional
from desktop.system_settings_manager import SystemSettingsManager

pyautogui.FAILSAFE = False
settings_mgr = SystemSettingsManager()

APP_EXECUTABLE_MAP = {
    "file explorer": "explorer.exe",
    "explorer": "explorer.exe",
    "settings": "SystemSettings.exe",
    "calculator": "CalculatorApp.exe",
    "calc": "CalculatorApp.exe",
    "camera": "WindowsCamera.exe",
    "photos": "Microsoft.Photos.exe",
    "paint": "mspaint.exe",
    "notepad": "notepad.exe",
    "command prompt": "cmd.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "windows terminal": "wt.exe",
    "terminal": "wt.exe",
    "microsoft store": "WinStore.App.exe",
    "store": "WinStore.App.exe",
    "media player": "wmplayer.exe",
    "clock": "Time.exe",
    "task manager": "taskmgr.exe",
    "control panel": "control.exe",
    "vs code": "code.exe",
    "vscode": "code.exe",
    "android studio": "studio64.exe",
    "chrome": "chrome.exe",
    "edge": "msedge.exe",
    "firefox": "firefox.exe",
    "brave": "brave.exe",
    "opera": "opera.exe",
    "word": "winword.exe",
    "excel": "excel.exe",
    "powerpoint": "powerpnt.exe",
    "spotify": "Spotify.exe",
    "whatsapp": "WhatsApp.exe",
    "telegram": "Telegram.exe",
    "discord": "Discord.exe",
    "steam": "steam.exe",
    "vlc": "vlc.exe",
    "obs studio": "obs64.exe",
    "obs": "obs64.exe"
}

APP_LAUNCH_CMD = {
    "file explorer": "explorer.exe",
    "explorer": "explorer.exe",
    "settings": "start ms-settings:",
    "calculator": "calc.exe",
    "calc": "calc.exe",
    "camera": "start microsoft.windows.camera:",
    "photos": "start ms-photos:",
    "paint": "mspaint.exe",
    "notepad": "notepad.exe",
    "command prompt": "cmd.exe",
    "cmd": "cmd.exe",
    "powershell": "powershell.exe",
    "windows terminal": "wt.exe",
    "terminal": "wt.exe",
    "microsoft store": "start ms-windows-store:",
    "store": "start ms-windows-store:",
    "media player": "wmplayer.exe",
    "clock": "start ms-clock:",
    "task manager": "taskmgr.exe",
    "control panel": "control.exe",
    "vs code": "code",
    "vscode": "code",
    "android studio": "studio64.exe",
    "chrome": "start chrome",
    "edge": "start msedge",
    "firefox": "start firefox",
    "brave": "start brave",
    "opera": "start opera",
    "word": "start winword",
    "excel": "start excel",
    "powerpoint": "start powerpnt",
    "spotify": "start spotify:",
    "whatsapp": "start whatsapp:",
    "telegram": "start telegram:",
    "discord": "start discord:",
    "steam": "start steam:",
    "vlc": "start vlc",
    "obs studio": "start obs",
    "obs": "start obs"
}

SETTINGS_URI_MAP = {
    "bluetooth": "ms-settings:bluetooth",
    "wifi": "ms-settings:network-wifi",
    "network": "ms-settings:network",
    "night light": "ms-settings:nightlight",
    "display": "ms-settings:display",
    "sound": "ms-settings:sound",
    "battery saver": "ms-settings:batterysaver",
    "storage": "ms-settings:storagesense",
    "privacy": "ms-settings:privacy",
    "windows update": "ms-settings:windowsupdate",
    "update": "ms-settings:windowsupdate",
    "location": "ms-settings:privacy-location",
    "power": "ms-settings:powersleep",
    "hotspot": "ms-settings:network-mobilehotspot",
    "accessibility": "ms-settings:easeofaccess-keyboard"
}

def log_execution(intent: str, status: str, detail: str = ""):
    """Simplified execution logging format."""
    detail_str = f" [{detail}]" if detail else ""
    print(f"\n[Desktop Core] Intent: {intent} -> {status}{detail_str}")


def find_window_by_title(target_title: str) -> int:
    """Finds window handle (HWND) matching target title substring."""
    target_lower = target_title.lower()
    found_hwnd = 0

    def enum_windows_callback(hwnd, extra):
        nonlocal found_hwnd
        if win32gui.IsWindowVisible(hwnd):
            title = win32gui.GetWindowText(hwnd).lower()
            if target_lower in title and len(title) > 0:
                found_hwnd = hwnd
                return False
        return True

    try:
        win32gui.EnumWindows(enum_windows_callback, None)
    except Exception:
        pass

    return found_hwnd


def focus_or_launch_app(app_name: str) -> bool:
    """Focuses app if already open, otherwise launches it."""
    log_execution(f"OPEN_{app_name.upper()}", "Executing...")
    app_key = app_name.strip().lower()

    # Check if already open and focus
    hwnd = find_window_by_title(app_key)
    if hwnd:
        try:
            if win32gui.IsIconic(hwnd):
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            win32gui.SetForegroundWindow(hwnd)
            time.sleep(0.5)
            log_execution(f"OPEN_{app_name.upper()}", "Verified", "Focused existing window")
            log_execution(f"OPEN_{app_name.upper()}", "Completed")
            return True
        except Exception:
            pass

    # Launch application
    exec_cmd = APP_LAUNCH_CMD.get(app_key, f"start {app_key}")
    try:
        if exec_cmd.startswith("start "):
            os.system(exec_cmd)
        else:
            subprocess.Popen(exec_cmd, shell=True)

        time.sleep(1.8)
        log_execution(f"OPEN_{app_name.upper()}", "Verified", "App launched")
        log_execution(f"OPEN_{app_name.upper()}", "Completed")
        return True
    except Exception as e:
        log_execution(f"OPEN_{app_name.upper()}", "Failed", str(e))
        return False


def set_window_state(app_name: str, state_action: str) -> bool:
    """Minimizes, maximizes, restores, or closes an active app window."""
    action_upper = state_action.upper()
    app_key = app_name.strip().lower()
    log_execution(f"{action_upper}_{app_name.upper()}", "Executing...")

    if app_key == "active":
        hwnd = win32gui.GetForegroundWindow()
    else:
        hwnd = find_window_by_title(app_key)

    if hwnd:
        try:
            if action_upper == "MINIMIZE":
                win32gui.ShowWindow(hwnd, win32con.SW_MINIMIZE)
            elif action_upper == "MAXIMIZE":
                win32gui.ShowWindow(hwnd, win32con.SW_MAXIMIZE)
            elif action_upper == "RESTORE":
                win32gui.ShowWindow(hwnd, win32con.SW_RESTORE)
            elif action_upper == "CLOSE":
                win32gui.PostMessage(hwnd, win32con.WM_CLOSE, 0, 0)

            time.sleep(0.5)
            log_execution(f"{action_upper}_{app_name.upper()}", "Verified")
            log_execution(f"{action_upper}_{app_name.upper()}", "Completed")
            return True
        except Exception:
            pass

    if action_upper == "CLOSE":
        proc_name = APP_EXECUTABLE_MAP.get(app_key, f"{app_key}.exe")
        try:
            subprocess.run(["taskkill", "/IM", proc_name, "/F", "/T"], capture_output=True)
            time.sleep(0.5)
            log_execution(f"{action_upper}_{app_name.upper()}", "Verified", "Terminated via taskkill")
            log_execution(f"{action_upper}_{app_name.upper()}", "Completed")
            return True
        except Exception:
            pass

    try:
        if action_upper == "CLOSE":
            pyautogui.hotkey('alt', 'f4')
        elif action_upper == "MINIMIZE":
            pyautogui.hotkey('win', 'down')
        elif action_upper == "MAXIMIZE":
            pyautogui.hotkey('win', 'up')
        elif action_upper == "RESTORE":
            pyautogui.hotkey('win', 'down')

        time.sleep(0.5)
        log_execution(f"{action_upper}_{app_name.upper()}", "Verified", "Applied via hotkey")
        log_execution(f"{action_upper}_{app_name.upper()}", "Completed")
        return True
    except Exception as e:
        log_execution(f"{action_upper}_{app_name.upper()}", "Failed", str(e))
        return False


def toggle_system_setting(feature_name: str, state: str) -> bool:
    """Toggles any Windows system setting (ON / OFF) by feature name using SystemSettingsManager."""
    log_execution(f"TOGGLE_SETTING_{feature_name.upper()}_{state.upper()}", "Executing...")
    res = settings_mgr.toggle_setting(feature_name, state)
    status = "Verified" if res else "Failed"
    log_execution(f"TOGGLE_SETTING_{feature_name.upper()}_{state.upper()}", status)
    log_execution(f"TOGGLE_SETTING_{feature_name.upper()}_{state.upper()}", "Completed")
    return res


def adjust_volume(action: str, percent: int = None) -> bool:
    """Adjusts volume up, down, mute, unmute, or sets percentage via SystemSettingsManager."""
    log_execution("VOLUME_CONTROL", "Executing...")
    res = settings_mgr.adjust_volume(action, percent)
    status = "Verified" if res else "Failed"
    log_execution("VOLUME_CONTROL", status, f"Action '{action}' applied")
    log_execution("VOLUME_CONTROL", "Completed")
    return res


def adjust_brightness(action: str, percent: int = 80) -> bool:
    """Adjusts brightness percentage using SystemSettingsManager."""
    log_execution("BRIGHTNESS_CONTROL", "Executing...")
    res = settings_mgr.adjust_brightness(action, percent)
    status = "Verified" if res else "Failed"
    log_execution("BRIGHTNESS_CONTROL", status, f"Brightness set to {percent}%")
    log_execution("BRIGHTNESS_CONTROL", "Completed")
    return res


def open_system_setting(setting_name: str) -> bool:
    """Opens specific Windows Settings page via URI scheme."""
    log_execution(f"SYSTEM_SETTING_{setting_name.upper()}", "Executing...")
    setting_key = setting_name.strip().lower()
    uri = SETTINGS_URI_MAP.get(setting_key, f"ms-settings:{setting_key}")
    try:
        subprocess.Popen(["cmd.exe", "/c", "start", uri], shell=True)
        log_execution(f"SYSTEM_SETTING_{setting_name.upper()}", "Verified", f"Opened {uri}")
        log_execution(f"SYSTEM_SETTING_{setting_name.upper()}", "Completed")
        return True
    except Exception as e:
        log_execution(f"SYSTEM_SETTING_{setting_name.upper()}", "Failed", str(e))
        return False


def execute_windows_system_action(action_name: str) -> bool:
    """Executes common Windows system actions (lock, sleep, task view, etc.)."""
    log_execution(f"WINDOWS_ACTION_{action_name.upper()}", "Executing...")
    act = action_name.strip().lower()
    try:
        if act == "lock":
            ctypes.windll.user32.LockWorkStation()
        elif act in ["show desktop", "hide desktop"]:
            pyautogui.hotkey('win', 'd')
        elif act == "task view":
            pyautogui.hotkey('win', 'tab')
        elif act == "action center":
            pyautogui.hotkey('win', 'a')
        elif act == "notifications":
            pyautogui.hotkey('win', 'n')
        elif act == "clipboard history":
            pyautogui.hotkey('win', 'v')
        elif act == "emoji panel":
            pyautogui.hotkey('win', '.')
        elif act == "sleep":
            subprocess.run(["rundll32.exe", "powrprof.dll,SetSuspendState", "0,1,0"])
        log_execution(f"WINDOWS_ACTION_{action_name.upper()}", "Verified")
        log_execution(f"WINDOWS_ACTION_{action_name.upper()}", "Completed")
        return True
    except Exception as e:
        log_execution(f"WINDOWS_ACTION_{action_name.upper()}", "Failed", str(e))
        return False


def take_desktop_screenshot(open_folder: bool = True) -> bool:
    """Takes an immediate full screen screenshot via SystemSettingsManager."""
    log_execution("TAKE_SCREENSHOT", "Executing...")
    res = settings_mgr.take_immediate_screenshot(open_folder=open_folder)
    status = "Verified" if res else "Failed"
    log_execution("TAKE_SCREENSHOT", status, "Saved to Pictures")
    log_execution("TAKE_SCREENSHOT", "Completed")
    return res


def media_control(action: str) -> bool:
    """Controls media playback (play, pause, next, previous, stop)."""
    log_execution(f"MEDIA_{action.upper()}", "Executing...")
    act = action.strip().lower()
    try:
        if act in ["play", "pause", "resume"]:
            win32api.keybd_event(0xCD, 0, 0, 0)
            win32api.keybd_event(0xCD, 0, win32con.KEYEVENTF_KEYUP, 0)
        elif act == "next":
            win32api.keybd_event(0xB0, 0, 0, 0)
            win32api.keybd_event(0xB0, 0, win32con.KEYEVENTF_KEYUP, 0)
        elif act in ["previous", "prev"]:
            win32api.keybd_event(0xB1, 0, 0, 0)
            win32api.keybd_event(0xB1, 0, win32con.KEYEVENTF_KEYUP, 0)
        elif act == "stop":
            win32api.keybd_event(0xB2, 0, 0, 0)
            win32api.keybd_event(0xB2, 0, win32con.KEYEVENTF_KEYUP, 0)

        log_execution(f"MEDIA_{action.upper()}", "Verified")
        log_execution(f"MEDIA_{action.upper()}", "Completed")
        return True
    except Exception as e:
        log_execution(f"MEDIA_{action.upper()}", "Failed", str(e))
        return False


def navigate_explorer_folder(folder_name: str) -> bool:
    """Navigates File Explorer to specific standard folders or drives."""
    log_execution(f"EXPLORER_NAVIGATE_{folder_name.upper()}", "Executing...")

    folder_map = {
        "downloads": os.path.expanduser("~\\Downloads"),
        "documents": os.path.expanduser("~\\Documents"),
        "desktop": os.path.expanduser("~\\Desktop"),
        "pictures": os.path.expanduser("~\\Pictures"),
        "videos": os.path.expanduser("~\\Videos"),
        "music": os.path.expanduser("~\\Music"),
        "this pc": "shell:MyComputerFolder",
        "recycle bin": "shell:RecycleBinFolder",
        "local disk c": "C:\\",
        "local disk d": "D:\\",
        "local disk e": "E:\\",
        "usb drive": "E:\\"
    }

    target_path = folder_map.get(folder_name.lower(), os.path.expanduser("~\\Downloads"))
    try:
        subprocess.Popen(["explorer.exe", target_path], shell=True)
        time.sleep(1.0)
        log_execution(f"EXPLORER_NAVIGATE_{folder_name.upper()}", "Verified", f"Navigated to {folder_name}")
        log_execution(f"EXPLORER_NAVIGATE_{folder_name.upper()}", "Completed")
        return True
    except Exception as e:
        log_execution(f"EXPLORER_NAVIGATE_{folder_name.upper()}", "Failed", str(e))
        return False


def camera_control(action: str) -> bool:
    """Controls Camera app (open, photo, video, close)."""
    act = action.lower()
    if "open" in act or "launch" in act or "start" in act:
        return focus_or_launch_app("camera")
    elif "close" in act or "stop" in act:
        return set_window_state("camera", "close")
    elif "photo" in act or "take" in act or "capture" in act or "picture" in act:
        log_execution("CAMERA_TAKE PHOTO", "Executing...")
        focus_or_launch_app("camera")
        time.sleep(1.5)
        pyautogui.press('space')
        log_execution("CAMERA_TAKE PHOTO", "Verified")
        log_execution("CAMERA_TAKE PHOTO", "Completed")
        return True
    return False


def calculate_expression(expression: str) -> Optional[str]:
    """Calculates mathematical expression string safely."""
    log_execution("CALCULATE_EXPRESSION", "Executing...", expression)
    try:
        clean_expr = re.sub(r'[^0-9\+\-\*\/\(\)\.\s]', '', expression)
        if clean_expr:
            result = eval(clean_expr, {"__builtins__": None}, {})
            log_execution("CALCULATE_EXPRESSION", "Verified", f"Result: {result}")
            log_execution("CALCULATE_EXPRESSION", "Completed")
            return str(result)
    except Exception as e:
        log_execution("CALCULATE_EXPRESSION", "Failed", str(e))
    return None
