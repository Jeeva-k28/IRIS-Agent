from website_workflows.base_workflow import BaseWebsiteWorkflow
import time
import pyautogui
import webbrowser as wb

class XWorkflow(BaseWebsiteWorkflow):
    """Workflow dedicated strictly to X (Twitter) interactions."""

    def __init__(self):
        super().__init__(domain="x.com", name="X")

    def can_handle(self, domain_or_title: str) -> bool:
        if not domain_or_title:
            return False
        d = domain_or_title.lower()
        return "x.com" in d or "twitter.com" in d or "twitter" in d or "x" in d

    def execute_step(self, step: dict) -> bool:
        action = step.get("action", "").upper()
        target = step.get("target", "")

        if action == "OPEN":
            wb.open("https://x.com")
            time.sleep(2.5)
            return True

        elif action == "SEARCH":
            pyautogui.press('/')
            time.sleep(0.4)
            pyautogui.write(target, interval=0.05)
            pyautogui.press('enter')
            return True

        return False
