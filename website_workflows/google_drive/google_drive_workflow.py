from website_workflows.base_workflow import BaseWebsiteWorkflow
import time
import pyautogui
import webbrowser as wb

class GoogleDriveWorkflow(BaseWebsiteWorkflow):
    """Workflow dedicated strictly to Google Drive interactions."""

    def __init__(self):
        super().__init__(domain="drive.google.com", name="Google Drive")

    def execute_step(self, step: dict) -> bool:
        action = step.get("action", "").upper()
        target = step.get("target", "")

        if action == "OPEN":
            wb.open("https://drive.google.com")
            time.sleep(3.0)
            return True

        elif action == "SEARCH":
            pyautogui.press('/')
            time.sleep(0.4)
            pyautogui.write(target, interval=0.05)
            pyautogui.press('enter')
            return True

        elif action == "CREATE_FOLDER":
            pyautogui.press('c')
            time.sleep(0.3)
            pyautogui.press('f')
            return True

        return False
