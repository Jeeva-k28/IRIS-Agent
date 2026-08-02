from website_workflows.base_workflow import BaseWebsiteWorkflow
import time
import pyautogui
import webbrowser as wb

class GoogleWorkflow(BaseWebsiteWorkflow):
    """Workflow dedicated strictly to Google search interactions."""

    def __init__(self):
        super().__init__(domain="google.com", name="Google")

    def execute_step(self, step: dict) -> bool:
        action = step.get("action", "").upper()
        target = step.get("target", "")

        if action == "OPEN":
            self.open_website()
            return True

        elif action == "SEARCH":
            pyautogui.hotkey('ctrl', 'l')
            time.sleep(0.3)
            pyautogui.write(target, interval=0.05)
            pyautogui.press('enter')
            time.sleep(2.0)
            return True

        return False
