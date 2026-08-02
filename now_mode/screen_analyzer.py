import os
import win32gui
import pyautogui
from typing import Dict, Any, List
from now_mode.vision_engine import VisionEngine

class CurrentScreenAnalyzer:
    """Captures current active screen and extracts application context, window title, and visible text/elements."""

    def __init__(self, temp_image_path: str = "now_screen_temp.png"):
        self.temp_image_path = temp_image_path
        self.vision_engine = VisionEngine()

    def get_active_window_title(self) -> str:
        """Returns active foreground window title."""
        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            return title.strip() if title else "Desktop"
        except Exception:
            return "Desktop"

    def analyze_screen(self) -> Dict[str, Any]:
        """Captures screenshot and returns structured screen state."""
        window_title = self.get_active_window_title()
        
        try:
            img = pyautogui.screenshot()
            img.save(self.temp_image_path)
            elements = self.vision_engine.extract_text_and_boxes(self.temp_image_path)
        except Exception as e:
            print(f"Screen capture notice: {e}")
            elements = []

        return {
            "window_title": window_title,
            "elements": elements,
            "image_path": self.temp_image_path
        }
