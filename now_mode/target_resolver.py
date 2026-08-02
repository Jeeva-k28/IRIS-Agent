import re
import json
import win32gui
from typing import Dict, Any, Optional, Tuple, List
from now_mode.semantic_ui_parser import CurrentPageSemanticModel
from now_mode.uia_inspector import UIAInspector

try:
    from g4f.client import Client
except ImportError:
    Client = None


def resolve_target_with_ai(command: str, semantic_model: CurrentPageSemanticModel) -> Optional[Dict[str, Any]]:
    """Uses GPT-4o AI Vision Reasoning Engine to analyze visible screen elements and instruct the agent on exact actions."""
    if not Client:
        return None

    try:
        client = Client()

        elements_summary = []
        for el in semantic_model.elements[:30]:  # Top 30 visible screen elements
            txt = el.get("text", "").strip()
            if txt:
                elements_summary.append({
                    "text": txt,
                    "cx": el.get("cx", 0),
                    "cy": el.get("cy", 0)
                })

        prompt = (
            f"User Command: '{command}'\n"
            f"Active Window: '{semantic_model.window_title}'\n"
            f"Elements: {json.dumps(elements_summary[:20])}\n\n"
            f"Return JSON only: {{\"type\": \"SEEK_VIDEO\"|\"RESTART_VIDEO\"|\"TOGGLE_PLAYBACK\"|\"REFRESH_PAGE\"|\"NAVIGATE_LINK\"|\"PLAY_NTH_VIDEO\"|\"CLICK\"|\"SCROLL\", \"target\": \"name\", \"minute\": N, \"ordinal\": N, \"coords\": [x,y]}}"
        )

        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are IRIS AI Screen Vision Reasoning Engine. Return raw JSON only."},
                {"role": "user", "content": prompt}
            ]
        )

        content = response.choices[0].message.content.strip()
        if content.startswith("```"):
            content = re.sub(r'^```(json)?\n', '', content)
            content = re.sub(r'\n```$', '', content).strip()

        result = json.loads(content)
        if isinstance(result, dict) and "type" in result:
            print(f"[AI Screen Reasoning]: AI instructed action '{result['type']}' for target '{result.get('target', command)}'")
            return result

    except Exception:
        pass

    return None


class TargetResolver:
    """Universal Target Resolver that resolves target elements and cards on the CURRENT page/window on screen."""

    def __init__(self):
        self.uia_inspector = UIAInspector()

    def resolve(self, command: str, semantic_model: CurrentPageSemanticModel) -> Dict[str, Any]:
        cmd_l = command.strip().lower()

        # 1. Fast Local Rule Resolution FIRST

        # 1.1 Check Seek Video (Minute N) FIRST before Restart
        seek_match = re.search(r'(?:from|at|to)\s*(\d+)|(\d+)\s*(?:minute|min)', cmd_l)
        if seek_match:
            min_val = int(seek_match.group(1) or seek_match.group(2))
            return {"type": "SEEK_VIDEO", "minute": min_val, "target": f"Seek to {min_val} minute"}

        # 1.2 Restart / Beginning Video
        if any(kw in cmd_l for kw in ["from beginning", "from start", "restart this video", "restart video", "play from beginning", "play from first", "from zero", "from 0"]):
            return {"type": "RESTART_VIDEO", "target": "YouTube Video Player (Beginning)"}

        # 1.3 Resume / Pause / Stop / Toggle Playback
        if any(kw in cmd_l for kw in ["resume", "pause", "stop this video", "stop video", "play this video", "toggle playback"]):
            return {"type": "TOGGLE_PLAYBACK", "target": "YouTube Video Player (Toggle)"}

        # 1.4 Refresh Page
        if any(kw in cmd_l for kw in ["refresh", "reload"]):
            return {"type": "REFRESH_PAGE", "target": "Active Page"}

        # 1.5 Explicit Song / Video Title Play Commands (e.g. "now play karuppu koda vaa")
        if cmd_l.startswith("now play ") or cmd_l.startswith("play "):
            song_title = re.sub(r'^(now\s+)?play\s*', '', cmd_l).strip()
            if song_title and song_title not in ["video", "song", "this video", "first video"]:
                coords = self._find_element_coords([song_title], semantic_model.elements)
                if not coords:
                    try:
                        hwnd = win32gui.GetForegroundWindow()
                        coords = self.uia_inspector.find_element_center_by_name(hwnd, song_title)
                    except Exception:
                        pass
                return {"type": "CLICK", "target": song_title, "coords": coords}

        # 1.6 Play Nth Video on Screen (ONLY when explicitly requested by user: "play 1st video", "play second video", etc.)
        nth_video_match = re.search(r'play\s+(the\s+)?(\d+|first|1st|second|2nd|third|3rd|fourth|4th)\s+video', cmd_l)
        if nth_video_match:
            val = nth_video_match.group(2).lower()
            idx = 1
            if val in ["first", "1st"]:
                idx = 1
            elif val in ["second", "2nd"]:
                idx = 2
            elif val in ["third", "3rd"]:
                idx = 3
            elif val in ["fourth", "4th"]:
                idx = 4
            elif val.isdigit():
                idx = int(val)
            coords = self._find_element_coords([f"video #{idx}", "video", "play"], semantic_model.elements)
            return {"type": "PLAY_NTH_VIDEO", "ordinal": idx, "coords": coords, "target": f"Video #{idx} on screen"}

        # 1.7 Scroll Commands
        elif "scroll" in cmd_l:
            direction = "down" if any(w in cmd_l for w in ["down", "bottom"]) else "up"
            return {"type": "SCROLL", "direction": direction, "target": f"scroll {direction}"}

        # 1.8 Universal Click / Open / Select Element & Card Target Match (Strictly on CURRENT page!)
        elif any(verb in cmd_l for verb in ["click", "open", "select"]):
            target_name = re.sub(r'^(now\s+)?(click|open|select)\s*', '', cmd_l).strip()

            # First, check OCR / Page Elements inside active foreground window bounds
            coords = self._find_element_coords([target_name], semantic_model.elements)

            # Second, if not found in OCR elements, inspect via UIA Inspector across active window child controls
            if not coords:
                try:
                    hwnd = win32gui.GetForegroundWindow()
                    coords = self.uia_inspector.find_element_center_by_name(hwnd, target_name)
                except Exception:
                    pass

            return {"type": "CLICK", "target": target_name, "coords": coords}

        # 2. Try AI Vision Reasoning Fallback if rule didn't match
        ai_resolved = resolve_target_with_ai(command, semantic_model)
        if ai_resolved:
            return ai_resolved

        coords = self._find_element_coords([cmd_l], semantic_model.elements)
        return {"type": "CLICK", "target": cmd_l, "coords": coords}

    def _find_element_coords(self, keywords: List[str], elements: List[Dict[str, Any]]) -> Optional[Tuple[int, int]]:
        # Get active window bounds to filter elements within active window
        win_rect = None
        try:
            hwnd = win32gui.GetForegroundWindow()
            if hwnd:
                win_rect = win32gui.GetWindowRect(hwnd)
        except Exception:
            pass

        for kw in keywords:
            kw_l = kw.lower()
            clean_kw = re.sub(r'\b(button|link|icon|tab|option|card)\b', '', kw_l, flags=re.IGNORECASE).strip()
            if not clean_kw:
                clean_kw = kw_l

            kw_words = set(clean_kw.split())

            # 1. Exact or Substring match
            for el in elements:
                cx, cy = el.get("cx", 0), el.get("cy", 0)
                if win_rect and not (win_rect[0] <= cx <= win_rect[2] and win_rect[1] <= cy <= win_rect[3]):
                    continue

                txt_l = el.get("text", "").lower().strip()
                if not txt_l:
                    continue
                if clean_kw in txt_l or txt_l in clean_kw:
                    return (cx, cy)

            # 2. Word Token Match
            for el in elements:
                cx, cy = el.get("cx", 0), el.get("cy", 0)
                if win_rect and not (win_rect[0] <= cx <= win_rect[2] and win_rect[1] <= cy <= win_rect[3]):
                    continue

                txt_l = el.get("text", "").lower().strip()
                if not txt_l:
                    continue
                txt_words = set(txt_l.split())
                if kw_words and (kw_words.issubset(txt_words) or txt_words.issubset(kw_words)):
                    return (cx, cy)

        return None
