import time
import pyautogui
import webbrowser as wb

class BaseWebsiteWorkflow:
    """Abstract Base Class for website-specific workflows."""
    
    def __init__(self, domain: str, name: str):
        self.domain = domain
        self.name = name

    def can_handle(self, domain_or_title: str) -> bool:
        """Returns True if this workflow can handle the given domain or window title."""
        if not domain_or_title:
            return False
        return self.domain.lower() in domain_or_title.lower() or self.name.lower() in domain_or_title.lower()

    def open_website(self) -> None:
        """Opens the base URL of the website."""
        wb.open(f"https://www.{self.domain}")
        time.sleep(2.5)

    def execute_step(self, step: dict) -> bool:
        """Executes a single step in the website workflow. Override in subclasses."""
        raise NotImplementedError("Subclasses must implement execute_step")

    def observe_and_continue(self) -> None:
        """Observes the result of a step and prepares for the next action."""
        time.sleep(0.5)
