import unittest
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

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

class TestDesktopCoreExpanded(unittest.TestCase):
    """Expanded Regression Test Suite for Complete Windows Desktop Assistant Core."""

    def test_01_open_calculator(self):
        result = focus_or_launch_app("calculator")
        self.assertTrue(result, "Failed to open Calculator")

    def test_02_calculate_expression(self):
        result = calculate_expression("25 * 4 + 10")
        self.assertEqual(result, "110", "Failed mathematical calculation")

    def test_03_close_calculator(self):
        result = set_window_state("calculator", "close")
        self.assertTrue(result, "Failed to close Calculator")

    def test_04_open_notepad(self):
        result = focus_or_launch_app("notepad")
        self.assertTrue(result, "Failed to open Notepad")

    def test_05_minimize_restore_notepad(self):
        min_res = set_window_state("notepad", "minimize")
        self.assertTrue(min_res, "Failed to minimize Notepad")
        res_res = set_window_state("notepad", "restore")
        self.assertTrue(res_res, "Failed to restore Notepad")

    def test_06_close_notepad(self):
        result = set_window_state("notepad", "close")
        self.assertTrue(result, "Failed to close Notepad")

    def test_07_volume_controls(self):
        up_res = adjust_volume("up")
        self.assertTrue(up_res, "Failed Volume Up")
        down_res = adjust_volume("down")
        self.assertTrue(down_res, "Failed Volume Down")
        set_res = adjust_volume("set", percent=40)
        self.assertTrue(set_res, "Failed Set Volume Percentage")

    def test_08_brightness_controls(self):
        res = adjust_brightness("set", percent=80)
        self.assertTrue(res, "Failed Brightness Control")

    def test_09_settings_uris(self):
        bt_res = open_system_setting("bluetooth")
        self.assertTrue(bt_res, "Failed to open Bluetooth Settings")
        disp_res = open_system_setting("display")
        self.assertTrue(disp_res, "Failed to open Display Settings")
        set_window_state("settings", "close")

    def test_10_system_actions(self):
        desk_res = execute_windows_system_action("show desktop")
        self.assertTrue(desk_res, "Failed Show Desktop action")

    def test_11_screenshot_control(self):
        ss_res = take_desktop_screenshot(open_folder=False)
        self.assertTrue(ss_res, "Failed to take screenshot")

    def test_12_media_control(self):
        m_res = media_control("play")
        self.assertTrue(m_res, "Failed Media Play/Pause action")

    def test_13_explorer_navigation(self):
        down_res = navigate_explorer_folder("downloads")
        self.assertTrue(down_res, "Failed to navigate to Downloads")
        d_res = navigate_explorer_folder("local disk d")
        self.assertTrue(d_res, "Failed to navigate to Local Disk D")

    def test_14_camera_control(self):
        cam_res = camera_control("open")
        self.assertTrue(cam_res, "Failed to open Camera")
        photo_res = camera_control("take photo")
        self.assertTrue(photo_res, "Failed to take photo in Camera")
        close_res = camera_control("close")
        self.assertTrue(close_res, "Failed to close Camera")


if __name__ == "__main__":
    unittest.main()
