from typing import Dict, Any
from now_mode.screen_analyzer import CurrentScreenAnalyzer
from now_mode.semantic_ui_parser import SemanticUIParser
from now_mode.target_resolver import TargetResolver
from now_mode.now_executor import NowExecutor

class NowModeEngine:
    """Main Orchestrator for NOW MODE screen-aware intelligence."""

    def __init__(self):
        self.screen_analyzer = CurrentScreenAnalyzer()
        self.semantic_parser = SemanticUIParser()
        self.target_resolver = TargetResolver()
        self.now_executor = NowExecutor()

    def process_now_command(self, query: str) -> bool:
        """Processes a 'Now...' command by capturing screen, parsing UI, resolving target, and executing."""
        clean_cmd = query.strip()
        if clean_cmd.lower().startswith("now "):
            clean_cmd = clean_cmd[4:].strip()

        print(f"\n[NOW MODE Activated]: Analyzing current visible screen for command: '{clean_cmd}'...")

        # 1. Screen Analysis
        screen_data = self.screen_analyzer.analyze_screen()

        # 2. Semantic UI Understanding
        semantic_model = self.semantic_parser.parse(screen_data)
        print(f"  +-- Screen Context: App='{semantic_model.application}', Website='{semantic_model.website}', Window='{semantic_model.window_title}'")

        # 3. Target & Intent Resolution
        resolved = self.target_resolver.resolve(clean_cmd, semantic_model)

        # 4. Action Execution & Self Verification
        executed = self.now_executor.execute_resolved_target(resolved)
        print(f"[NOW MODE Completed]: Goal '{clean_cmd}' executed successfully!\n")
        return executed
