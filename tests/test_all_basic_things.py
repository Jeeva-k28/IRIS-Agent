import unittest
import sys
import os
import time

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

class TestAllBasicThingsOneByOne(unittest.TestCase):
    """Comprehensive One-By-One Self-Test Suite for IRIS Basic Capabilities."""

    def test_01_open_and_close_calculator(self):
        print("\n--- 1. Testing Open & Close Calculator ---")
        res1 = execute_single_command("open calculator")
        self.assertTrue(res1)
        time.sleep(1)
        res2 = execute_single_command("close calculator")
        self.assertTrue(res2)

    def test_02_open_and_close_notepad(self):
        print("\n--- 2. Testing Open & Close Notepad ---")
        res1 = execute_single_command("launch notepad")
        self.assertTrue(res1)
        time.sleep(1)
        res2 = execute_single_command("exit notepad")
        self.assertTrue(res2)

    def test_03_calculate_expression(self):
        print("\n--- 3. Testing Math Expression Calculation ---")
        res = calculate_expression("250 + 750")
        self.assertEqual(res, "1000")

    def test_04_volume_controls(self):
        print("\n--- 4. Testing System Volume Controls ---")
        res1 = execute_single_command("increase volume")
        self.assertTrue(res1)
        res2 = execute_single_command("decrease volume")
        self.assertTrue(res2)
        res3 = execute_single_command("set volume to 45")
        self.assertTrue(res3)

    def test_05_brightness_controls(self):
        print("\n--- 5. Testing Brightness Controls ---")
        res = execute_single_command("set brightness to 75 percent")
        self.assertTrue(res)

    def test_06_windows_settings(self):
        print("\n--- 6. Testing Windows Settings URIs ---")
        res1 = open_system_setting("bluetooth")
        self.assertTrue(res1)
        time.sleep(1)
        res2 = open_system_setting("display")
        self.assertTrue(res2)
        time.sleep(1)
        set_window_state("settings", "close")

    def test_07_file_explorer_navigation(self):
        print("\n--- 7. Testing File Explorer Navigation ---")
        res1 = execute_single_command("open downloads")
        self.assertTrue(res1)
        time.sleep(1)
        res2 = execute_single_command("open local disk d")
        self.assertTrue(res2)

    def test_08_windows_system_actions(self):
        print("\n--- 8. Testing System Actions (Show Desktop, Task View) ---")
        res1 = execute_windows_system_action("show desktop")
        self.assertTrue(res1)
        res2 = execute_windows_system_action("task view")
        self.assertTrue(res2)

    def test_09_screenshot(self):
        print("\n--- 9. Testing Screenshot Control ---")
        res = take_desktop_screenshot(open_folder=False)
        self.assertTrue(res)

    def test_10_media_controls(self):
        print("\n--- 10. Testing Media Play/Pause/Next ---")
        res1 = media_control("play")
        self.assertTrue(res1)
        res2 = media_control("next")
        self.assertTrue(res2)

    def test_11_camera_controls(self):
        print("\n--- 11. Testing Camera Open / Photo / Close ---")
        res1 = camera_control("open")
        self.assertTrue(res1)
        time.sleep(1)
        res2 = camera_control("take photo")
        self.assertTrue(res2)
        time.sleep(1)
        res3 = camera_control("close")
        self.assertTrue(res3)

    def test_12_natural_intent_parser(self):
        print("\n--- 12. Testing Natural Intent Model Builder ---")
        tm1 = build_human_task_model("open calculator")
        self.assertEqual(tm1.workspace, "calculator")
        tm2 = build_human_task_model("take screenshot")
        self.assertEqual(tm2.workspace, "Windows")

    def test_13_standalone_exit_interceptor(self):
        print("\n--- 13. Testing Standalone Exit Interceptor ---")
        self.assertFalse(process_full_query("exit"))
        self.assertFalse(process_full_query("stop"))
        self.assertFalse(process_full_query("quit"))
        self.assertFalse(process_full_query("offline"))
        self.assertFalse(process_full_query("go offline"))

if __name__ == "__main__":
    unittest.main()
