from dataclasses import dataclass, field
from typing import List, Dict, Any

@dataclass
class CurrentPageSemanticModel:
    """Internal semantic representation of current active page."""
    window_title: str
    application: str
    website: str
    visible_texts: List[str] = field(default_factory=list)
    elements: List[Dict[str, Any]] = field(default_factory=list)
    has_search_box: bool = False
    has_play_button: bool = False
    has_subscribe_button: bool = False
    has_download_button: bool = False

class SemanticUIParser:
    """Parses raw screen elements into a CurrentPageSemanticModel."""

    def parse(self, screen_data: Dict[str, Any]) -> CurrentPageSemanticModel:
        title = screen_data.get("window_title", "Desktop")
        elements = screen_data.get("elements", [])
        
        texts = [e["text"] for e in elements if e.get("text")]
        texts_lower = [t.lower() for t in texts]
        
        app = "Desktop"
        if "chrome" in title.lower():
            app = "Chrome"
        elif "edge" in title.lower():
            app = "Edge"
        elif "explorer" in title.lower():
            app = "Explorer"
        elif "calculator" in title.lower():
            app = "Calculator"

        website = ""
        if "youtube" in title.lower():
            website = "YouTube"
        elif "whatsapp" in title.lower():
            website = "WhatsApp"

        return CurrentPageSemanticModel(
            window_title=title,
            application=app,
            website=website,
            visible_texts=texts,
            elements=elements,
            has_search_box=any("search" in t for t in texts_lower),
            has_play_button=any("play" in t for t in texts_lower),
            has_subscribe_button=any("subscribe" in t for t in texts_lower),
            has_download_button=any("download" in t for t in texts_lower)
        )
