from website_workflows.base_workflow import BaseWebsiteWorkflow
import time
import pyautogui
import webbrowser as wb

class YouTubeWorkflow(BaseWebsiteWorkflow):
    """Workflow dedicated strictly to YouTube interactions."""

    def __init__(self):
        super().__init__(domain="youtube.com", name="YouTube")

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

        elif action in ["PLAY_NTH", "PLAY"]:
            ordinal = step.get("ordinal", 1)
            for _ in range(ordinal):
                pyautogui.press('tab')
                time.sleep(0.2)
            pyautogui.press('enter')
            return True

        elif action == "PAUSE" or action == "RESUME":
            pyautogui.press('k')
            return True

        elif action == "LIKE":
            pyautogui.press('i')
            return True

        elif action == "SUBSCRIBE":
            pyautogui.press('c')
            return True

        return False
