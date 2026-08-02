from website_workflows.base_workflow import BaseWebsiteWorkflow
import time
import pyautogui
import webbrowser as wb

class FacebookWorkflow(BaseWebsiteWorkflow):
    """Workflow dedicated strictly to Facebook interactions."""

    def __init__(self):
        super().__init__(domain="facebook.com", name="Facebook")

    def execute_step(self, step: dict) -> bool:
        action = step.get("action", "").upper()
        target = step.get("target", "")

        if action == "OPEN":
            self.open_website()
            return True

        elif action == "SEARCH":
            pyautogui.press('/')
            time.sleep(0.4)
            pyautogui.write(target, interval=0.05)
            pyautogui.press('enter')
            return True

        return False
