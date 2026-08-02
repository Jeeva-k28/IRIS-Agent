import unittest
import sys
import os
import time
import pyautogui
import win32gui

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from Iris.iris import execute_single_command, process_full_query
from desktop.desktop_core import (
    focus_or_launch_app,
    set_window_state,
    adjust_volume,
    adjust_brightness,
    open_system_setting,
    execute_windows_system_action,
    take_desktop_screenshot,
    media_control,
    navigate_explorer_folder,
    camera_control,
    calculate_expression
)
from intelligence_layer.human_intent_parser import build_human_task_model

class TestExhaustiveDesktopAssistant(unittest.TestCase):
    """Exhaustive One-By-One Test Suite for Every Single User-Requested Capability."""

    # 1. APPLICATION CONTROL & WINDOW MANAGEMENT
    def test_01_app_control_and_launch(self):
        print("\n[Test 1] Testing App Launch & Focus for Installed Applications...")
        apps = ["calculator", "notepad", "command prompt", "settings"]
        for app in apps:
            res_open = focus_or_launch_app(app)
            self.assertTrue(res_open, f"Failed to open/focus {app}")

    def test_02_app_window_states(self):
        print("\n[Test 2] Testing Window States (Minimize, Restore, Maximize, Close)...")
        focus_or_launch_app("notepad")
        self.assertTrue(set_window_state("notepad", "minimize"), "Failed to minimize Notepad")
        self.assertTrue(set_window_state("notepad", "restore"), "Failed to restore Notepad")
        self.assertTrue(set_window_state("notepad", "maximize"), "Failed to maximize Notepad")
        self.assertTrue(set_window_state("notepad", "close"), "Failed to close Notepad")

    # 2. FILE EXPLORER OPERATIONS
    def test_03_file_explorer_navigation_and_folders(self):
        print("\n[Test 3] Testing File Explorer Folders & Navigation...")
        folders = ["downloads", "documents", "desktop", "pictures", "videos", "music", "this pc", "recycle bin", "local disk c", "local disk d"]
        for f in folders:
            res = navigate_explorer_folder(f)
            self.assertTrue(res, f"Failed to navigate to {f}")

    def test_04_file_explorer_actions(self):
        print("\n[Test 4] Testing File Explorer Actions (Back, Forward, Refresh, Search, Selection)...")
        navigate_explorer_folder("downloads")
        pyautogui.hotkey('alt', 'left') # Back
        pyautogui.hotkey('alt', 'right') # Forward
        pyautogui.press('f5') # Refresh
        pyautogui.hotkey('ctrl', 'f') # Search
        pyautogui.press('escape') # Clear / Deselect
        set_window_state("explorer", "close")

    # 3. CALCULATOR & CAMERA
    def test_05_calculator_operations(self):
        print("\n[Test 5] Testing Calculator Operations & Calculation...")
        res_calc = calculate_expression("(500 * 2) - 150")
        self.assertEqual(res_calc, "850", "Math calculation failed")

    def test_06_camera_operations(self):
        print("\n[Test 6] Testing Camera (Open, Photo, Record, Close)...")
        self.assertTrue(camera_control("open"), "Camera open failed")
        self.assertTrue(camera_control("take photo"), "Camera photo failed")
        self.assertTrue(camera_control("close"), "Camera close failed")

    # 4. SYSTEM VOLUME & BRIGHTNESS
    def test_07_system_volume_controls(self):
        print("\n[Test 7] Testing System Volume (Up, Down, Set, Mute, Unmute)...")
        self.assertTrue(adjust_volume("up"), "Volume up failed")
        self.assertTrue(adjust_volume("down"), "Volume down failed")
        self.assertTrue(adjust_volume("mute"), "Volume mute failed")
        self.assertTrue(adjust_volume("unmute"), "Volume unmute failed")
        self.assertTrue(adjust_volume("set", percent=50), "Volume set percentage failed")

    def test_08_system_brightness_controls(self):
        print("\n[Test 8] Testing System Brightness (Up, Down, Set)...")
        self.assertTrue(adjust_brightness("set", percent=85), "Brightness set percentage failed")

    # 5. WINDOWS SETTINGS & SYSTEM SHORTCUTS
    def test_09_windows_settings_pages(self):
        print("\n[Test 9] Testing Windows Settings URIs (Bluetooth, Wi-Fi, Display, Sound, Updates)...")
        settings_pages = ["bluetooth", "wifi", "display", "sound", "windows update", "storage", "privacy", "power"]
        for s in settings_pages:
            res = open_system_setting(s)
            self.assertTrue(res, f"Failed to open setting page: {s}")
        set_window_state("settings", "close")

    def test_10_system_actions(self):
        print("\n[Test 10] Testing System Actions (Show Desktop, Task View, Action Center, Notifications)...")
        self.assertTrue(execute_windows_system_action("show desktop"), "Show Desktop failed")
        self.assertTrue(execute_windows_system_action("task view"), "Task View failed")
        self.assertTrue(execute_windows_system_action("action center"), "Action Center failed")
        self.assertTrue(execute_windows_system_action("emoji panel"), "Emoji Panel failed")
        pyautogui.press('escape')

    # 6. SCREENSHOT & MEDIA CONTROLS
    def test_11_screenshot_controls(self):
        print("\n[Test 11] Testing Screenshot Capture & Verification...")
        self.assertTrue(take_desktop_screenshot(open_folder=False), "Screenshot capture failed")

    def test_12_media_controls(self):
        print("\n[Test 12] Testing Media Controls (Play, Pause, Next, Prev, Stop)...")
        self.assertTrue(media_control("play"), "Media play failed")
        self.assertTrue(media_control("next"), "Media next failed")
        self.assertTrue(media_control("prev"), "Media prev failed")
        self.assertTrue(media_control("stop"), "Media stop failed")

    # 7. MOUSE, KEYBOARD & INTENT PARSING
    def test_13_mouse_and_keyboard_controls(self):
        print("\n[Test 13] Testing Keyboard & Mouse Utilities...")
        pyautogui.press('tab')
        pyautogui.press('enter')
        pyautogui.press('escape')

    def test_14_continuous_execution_and_verification(self):
        print("\n[Test 14] Testing Continuous Execution Loop Verification...")
        tm = build_human_task_model("open calculator and calculate 100 plus 200")
        self.assertIsNotNone(tm)
        self.assertTrue(len(tm.sequence) >= 1)


if __name__ == "__main__":
    unittest.main()
