from website_workflows.base_workflow import BaseWebsiteWorkflow
import time
import pyautogui
import webbrowser as wb

class WikipediaWorkflow(BaseWebsiteWorkflow):
    """Workflow dedicated strictly to Wikipedia interactions."""

    def __init__(self):
        super().__init__(domain="wikipedia.org", name="Wikipedia")

    def execute_step(self, step: dict) -> bool:
        action = step.get("action", "").upper()
        target = step.get("target", "")

        if action == "OPEN":
            self.open_website()
            return True

        elif action == "SEARCH":
            pyautogui.press('f')
            time.sleep(0.4)
            pyautogui.write(target, interval=0.05)
            pyautogui.press('enter')
            return True

        return False
