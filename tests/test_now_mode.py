import unittest
from now_mode.semantic_ui_parser import CurrentPageSemanticModel, SemanticUIParser
from now_mode.target_resolver import TargetResolver
from now_mode.now_executor import NowExecutor
from now_mode.now_mode import NowModeEngine

class TestNowMode(unittest.TestCase):

    def test_semantic_ui_parser_model_creation(self):
        parser = SemanticUIParser()
        raw_ocr_elements = [
            {"text": "Get", "cx": 400, "cy": 300},
            {"text": "Install", "cx": 500, "cy": 350},
            {"text": "Discover more", "cx": 600, "cy": 400}
        ]
        screen_data = {"window_title": "Microsoft Store", "elements": raw_ocr_elements}
        model = parser.parse(screen_data)
        self.assertIsInstance(model, CurrentPageSemanticModel)
        self.assertEqual(len(model.elements), 3)

    def test_target_resolver_exact_match(self):
        resolver = TargetResolver()
        model = CurrentPageSemanticModel(
            window_title="Microsoft Store",
            application="Desktop",
            website="",
            elements=[
                {"text": "Get", "cx": 400, "cy": 300},
                {"text": "Install", "cx": 500, "cy": 350}
            ]
        )

        res_get = resolver.resolve("now click Get button", model)
        self.assertEqual(res_get["type"], "CLICK")
        self.assertEqual(res_get["target"], "get button")
        self.assertEqual(res_get["coords"], (400, 300))

    def test_target_resolver_phrase_grouping(self):
        resolver = TargetResolver()
        model = CurrentPageSemanticModel(
            window_title="Browser Page",
            application="Chrome",
            website="",
            elements=[
                {"text": "Discover more", "cx": 600, "cy": 400}
            ]
        )

        res = resolver.resolve("Now click discover more", model)
        self.assertEqual(res["type"], "CLICK")
        self.assertEqual(res["target"], "discover more")
        self.assertEqual(res["coords"], (600, 400))

    def test_target_resolver_video_and_icon_intents(self):
        resolver = TargetResolver()
        model = CurrentPageSemanticModel(
            window_title="YouTube - Google Chrome",
            application="Chrome",
            website="YouTube",
            elements=[
                {"text": "Copilot", "cx": 850, "cy": 50}
            ]
        )

        res_copilot = resolver.resolve("now click chat with copilot", model)
        self.assertIn(res_copilot["type"], ["CLICK", "CLICK_ICON"])

        res_restart = resolver.resolve("Now play this video from beginning", model)
        self.assertEqual(res_restart["type"], "RESTART_VIDEO")

        res_seek_1 = resolver.resolve("Now play this video from 1", model)
        self.assertEqual(res_seek_1["type"], "SEEK_VIDEO")
        self.assertEqual(res_seek_1["minute"], 1)

        res_gmail = resolver.resolve("Now click Gmail button", model)
        self.assertEqual(res_gmail["type"], "CLICK")

    def test_now_executor(self):
        executor = NowExecutor()
        self.assertTrue(executor.execute_resolved_target({"type": "CLICK", "target": "Get button", "coords": (400, 300)}))
        self.assertTrue(executor.execute_resolved_target({"type": "CLICK", "target": "GitHub Copilot", "coords": (850, 50)}))
        self.assertTrue(executor.execute_resolved_target({"type": "RESTART_VIDEO"}))
        self.assertTrue(executor.execute_resolved_target({"type": "SEEK_VIDEO", "minute": 1}))

    def test_now_mode_engine(self):
        engine = NowModeEngine()
        res = engine.process_now_command("scroll down")
        self.assertTrue(res)

if __name__ == "__main__":
    unittest.main()
