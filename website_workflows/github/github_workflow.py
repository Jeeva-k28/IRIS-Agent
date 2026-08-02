from website_workflows.base_workflow import BaseWebsiteWorkflow
import time
import pyautogui
import webbrowser as wb

class GitHubWorkflow(BaseWebsiteWorkflow):
    """Workflow dedicated strictly to GitHub interactions."""

    def __init__(self):
        super().__init__(domain="github.com", name="GitHub")

    def execute_step(self, step: dict) -> bool:
        action = step.get("action", "").upper()
        target = step.get("target", "")

        if action == "OPEN":
            self.open_website()
            return True

        elif action == "SEARCH":
            pyautogui.press('/')
            time.sleep(0.4)
            pyautogui.hotkey('ctrl', 'a')
            pyautogui.write(target, interval=0.05)
            pyautogui.press('enter')
            time.sleep(2.0)
            return True

        elif action == "OPEN_REPO":
            pyautogui.press('tab')
            time.sleep(0.2)
            pyautogui.press('enter')
            return True

        elif action == "OPEN_ISSUES":
            pyautogui.hotkey('g', 'i')
            return True

        elif action == "OPEN_PULL_REQUESTS":
            pyautogui.hotkey('g', 'p')
            return True

        return False
