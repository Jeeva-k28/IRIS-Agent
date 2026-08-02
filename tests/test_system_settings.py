import unittest
from desktop.system_settings_manager import SystemSettingsManager
from desktop.desktop_core import toggle_system_setting, adjust_volume, adjust_brightness, take_desktop_screenshot

class TestSystemSettings(unittest.TestCase):

    def setUp(self):
        self.mgr = SystemSettingsManager()

    def test_settings_manager_instance(self):
        self.assertIsNotNone(self.mgr)

    def test_toggle_bluetooth_on_off(self):
        res_on = self.mgr.toggle_setting("bluetooth", "on")
        self.assertTrue(res_on)
        res_off = self.mgr.toggle_setting("bluetooth", "off")
        self.assertTrue(res_off)

    def test_toggle_wifi_on_off(self):
        res_on = self.mgr.toggle_setting("wifi", "on")
        self.assertTrue(res_on)

    def test_toggle_night_light(self):
        res = self.mgr.toggle_setting("night light", "on")
        self.assertTrue(res)

    def test_toggle_dark_mode(self):
        res = self.mgr.toggle_setting("dark mode", "on")
        self.assertTrue(res)

    def test_volume_adjustments(self):
        res_up = self.mgr.adjust_volume("up")
        self.assertTrue(res_up)
        res_set = self.mgr.adjust_volume("set", percent=75)
        self.assertTrue(res_set)

    def test_brightness_adjustments(self):
        res_set = self.mgr.adjust_brightness("set", percent=80)
        self.assertTrue(res_set)

    def test_immediate_screenshot(self):
        res = self.mgr.take_immediate_screenshot(open_folder=False)
        self.assertTrue(res)

    def test_desktop_core_integration(self):
        self.assertTrue(toggle_system_setting("bluetooth", "on"))
        self.assertTrue(adjust_volume("up"))
        self.assertTrue(adjust_brightness("set", percent=75))
        self.assertTrue(take_desktop_screenshot(open_folder=False))

    def test_direct_query_interceptor(self):
        from Iris.iris import handle_direct_system_settings_query
        self.assertTrue(handle_direct_system_settings_query("now take screenshot"))
        self.assertTrue(handle_direct_system_settings_query("now turn on bluetooth"))
        self.assertTrue(handle_direct_system_settings_query("turn off wifi"))
        self.assertTrue(handle_direct_system_settings_query("volume up"))
        self.assertTrue(handle_direct_system_settings_query("set brightness to 80"))

if __name__ == "__main__":
    unittest.main()
