from website_workflows.base_workflow import BaseWebsiteWorkflow
import time
import pyautogui
import webbrowser as wb

class GmailWorkflow(BaseWebsiteWorkflow):
    """Workflow dedicated strictly to Gmail interactions."""

    def __init__(self):
        super().__init__(domain="mail.google.com", name="Gmail")

    def execute_step(self, step: dict) -> bool:
        action = step.get("action", "").upper()
        target = step.get("target", "")

        if action == "OPEN":
            wb.open("https://mail.google.com")
            time.sleep(3.0)
            return True

        elif action == "SEARCH_MAIL" or action == "SEARCH":
            pyautogui.press('/')
            time.sleep(0.4)
            pyautogui.write(target, interval=0.05)
            pyautogui.press('enter')
            return True

        elif action == "COMPOSE":
            pyautogui.press('c')
            return True

        elif action == "REPLY":
            pyautogui.press('r')
            return True

        elif action == "DELETE":
            pyautogui.press('#')
            return True

        return False
