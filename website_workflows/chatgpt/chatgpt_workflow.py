from website_workflows.base_workflow import BaseWebsiteWorkflow
import time
import pyautogui
import webbrowser as wb

class ChatGPTWorkflow(BaseWebsiteWorkflow):
    """Workflow dedicated strictly to ChatGPT interactions."""

    def __init__(self):
        super().__init__(domain="chatgpt.com", name="ChatGPT")

    def execute_step(self, step: dict) -> bool:
        action = step.get("action", "").upper()
        target = step.get("target", "")

        if action == "OPEN":
            self.open_website()
            return True

        elif action in ["SEND_PROMPT", "PROMPT", "SEARCH"]:
            time.sleep(0.5)
            pyautogui.write(target, interval=0.04)
            time.sleep(0.3)
            pyautogui.press('enter')
            return True

        elif action == "NEW_CHAT":
            pyautogui.hotkey('ctrl', 'shift', 'o')
            return True

        return False
