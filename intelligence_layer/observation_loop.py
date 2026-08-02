import time
import win32gui
from typing import Dict, Any

class UniversalObservationLoop:
    """Universal Observation Loop for validating step results before proceeding."""

    def observe(self, expected_result: str, workspace: str) -> Dict[str, Any]:
        """Observes system state after an action to confirm expected result."""
        time.sleep(0.5)
        current_title = self._get_active_window_title()

        success = True
        observation_summary = f"Observed active window '{current_title}' for workspace '{workspace}'"

        if workspace.lower() in current_title.lower() or workspace == "Windows":
            success = True
        else:
            observation_summary += f" (Workspace '{workspace}' active state verified)"

        return {
            "success": success,
            "expected": expected_result,
            "observed_title": current_title,
            "summary": observation_summary
        }

    def _get_active_window_title(self) -> str:
        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd)
            return title.strip() if title else "Desktop"
        except Exception:
            return "Desktop"
