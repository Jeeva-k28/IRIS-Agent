import os
try:
    import pytesseract
except ImportError:
    pytesseract = None
from PIL import Image
from typing import Dict, Any, List, Tuple

class VisionEngine:
    """Modular Vision Engine supporting OCR word extraction and multi-word phrase bounding box grouping."""

    def __init__(self, provider: str = "tesseract"):
        self.provider = provider

    def extract_text_and_boxes(self, image_path: str) -> List[Dict[str, Any]]:
        """Extracts visible text, confidence, and bounding boxes (x, y, w, h) from screen image, including multi-word phrase groupings."""
        elements = []
        if not os.path.exists(image_path) or not pytesseract:
            return elements

        try:
            img = Image.open(image_path)
            data = pytesseract.image_to_data(img, output_type=pytesseract.Output.DICT)
            n_boxes = len(data['text'])

            word_elements = []
            for i in range(n_boxes):
                text = data['text'][i].strip()
                try:
                    conf = int(data['conf'][i])
                except (ValueError, TypeError):
                    conf = 0
                if text and conf > 25:
                    word_obj = {
                        "text": text,
                        "confidence": conf,
                        "x": data['left'][i],
                        "y": data['top'][i],
                        "w": data['width'][i],
                        "h": data['height'][i],
                        "cx": data['left'][i] + data['width'][i] // 2,
                        "cy": data['top'][i] + data['height'][i] // 2,
                        "line": data.get('line_num', [0]*n_boxes)[i],
                        "block": data.get('block_num', [0]*n_boxes)[i]
                    }
                    elements.append(word_obj)
                    word_elements.append(word_obj)

            # Group adjacent words on the same line into multi-word phrases (e.g. "Discover more", "Chat with Copilot")
            n_words = len(word_elements)
            for i in range(n_words):
                phrase_text = word_elements[i]["text"]
                min_x = word_elements[i]["x"]
                min_y = word_elements[i]["y"]
                max_r = word_elements[i]["x"] + word_elements[i]["w"]
                max_b = word_elements[i]["y"] + word_elements[i]["h"]
                curr_line = word_elements[i]["line"]
                curr_block = word_elements[i]["block"]

                for j in range(i + 1, min(i + 6, n_words)):
                    if word_elements[j]["line"] == curr_line and word_elements[j]["block"] == curr_block:
                        # Ensure words are horizontally adjacent (within 50 pixels)
                        if word_elements[j]["x"] - max_r < 50:
                            phrase_text += " " + word_elements[j]["text"]
                            max_r = max(max_r, word_elements[j]["x"] + word_elements[j]["w"])
                            max_b = max(max_b, word_elements[j]["y"] + word_elements[j]["h"])
                            min_y = min(min_y, word_elements[j]["y"])

                            elements.append({
                                "text": phrase_text,
                                "confidence": (word_elements[i]["confidence"] + word_elements[j]["confidence"]) // 2,
                                "x": min_x,
                                "y": min_y,
                                "w": max_r - min_x,
                                "h": max_b - min_y,
                                "cx": min_x + (max_r - min_x) // 2,
                                "cy": min_y + (max_b - min_y) // 2
                            })

        except Exception as e:
            print(f"[VisionEngine notice]: {e}")

        return elements
