import re
import json
from typing import Tuple, Dict, Any, List
from intelligence_layer.task_model import TaskModel, TaskStep
try:
    from g4f.client import Client
except ImportError:
    Client = None

ORDINAL_MAP = {
    "first": 1, "1st": 1, "one": 1,
    "second": 2, "2nd": 2, "two": 2,
    "third": 3, "3rd": 3, "three": 3,
    "fourth": 4, "4th": 4, "four": 4,
    "fifth": 5, "5th": 5, "five": 5,
    "last": -1, "latest": 1, "newest": 1, "oldest": -1
}

OPEN_SYNONYMS = ["open", "launch", "start", "run", "bring up", "show"]
CLOSE_SYNONYMS = ["close", "exit", "quit", "terminate"]

EXPLORER_KEYWORDS = [
    "file explorer", "explorer", "downloads", "documents", "desktop",
    "pictures", "videos", "music", "recycle bin", "local disk c",
    "local disk d", "local disk e", "this pc", "usb drive"
]

def extract_ordinal(text: str) -> Tuple[int, str]:
    text_lower = text.lower()
    for key, val in ORDINAL_MAP.items():
        pattern = r'\b' + re.escape(key) + r'\b'
        if re.search(pattern, text_lower):
            cleaned = re.sub(pattern, '', text, flags=re.IGNORECASE).strip()
            return val, cleaned
    match = re.search(r'\b(\d+)(st|nd|rd|th)?\b', text_lower)
    if match:
        val = int(match.group(1))
        cleaned = re.sub(r'\b' + re.escape(match.group(0)) + r'\b', '', text, flags=re.IGNORECASE).strip()
        return val, cleaned
    return 1, text


def decompose_speech_with_ai(query: str, current_workspace: str = "UNKNOWN") -> TaskModel:
    """Uses GPT-4o AI Context Engine to decompose complex human natural speech into exact structured steps."""
    if not query or not query.strip():
        return None

    raw = query.strip()
    raw_lower = raw.lower()

    if Client:
        try:
            client = Client()
            prompt = (
                f"Decompose the following user speech request into an ordered JSON array of execution steps.\n"
                f"User Request: '{raw}'\n"
                f"Active Workspace Context: '{current_workspace}'\n\n"
                f"Return ONLY valid JSON array with keys: 'workspace', 'action' (OPEN|CLOSE|TYPE|ENTER|SEARCH|GO|SELECT|PLAY|SET), 'target', 'parameters'.\n"
                f"Example for 'Open Calculator and calculate 25 times 18':\n"
                f"[\n"
                f"  {{\"workspace\": \"Calculator\", \"action\": \"OPEN\", \"target\": \"Calculator\", \"parameters\": {{}}}},\n"
                f"  {{\"workspace\": \"Calculator\", \"action\": \"TYPE\", \"target\": \"25 * 18\", \"parameters\": {{\"text\": \"25 * 18\"}}}},\n"
                f"  {{\"workspace\": \"Calculator\", \"action\": \"ENTER\", \"target\": \"Calculate\", \"parameters\": {{}}}}\n"
                f"]"
            )
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": "You are IRIS AI Task Planner. Output raw JSON array only."},
                    {"role": "user", "content": prompt}
                ]
            )
            content = response.choices[0].message.content.strip()

            # Clean JSON markdown blocks if present
            if content.startswith("```"):
                content = re.sub(r'^```(json)?\n', '', content)
                content = re.sub(r'\n```$', '', content).strip()

            steps_data = json.loads(content)
            if isinstance(steps_data, list) and len(steps_data) > 0:
                task_steps = []
                primary_workspace = steps_data[0].get("workspace", "Desktop")

                for idx, s in enumerate(steps_data, start=1):
                    ws = s.get("workspace", primary_workspace)
                    act = s.get("action", "EXECUTE").upper()
                    tgt = s.get("target", "")
                    params = s.get("parameters", {})
                    task_steps.append(TaskStep(
                        step_number=idx,
                        workspace=ws,
                        action=act,
                        target=tgt,
                        parameters=params if isinstance(params, dict) else {},
                        expected_result=f"{act} {tgt} in {ws}"
                    ))

                return TaskModel(
                    raw_query=raw,
                    primary_goal=f"AI Executing: '{raw}'",
                    workspace=primary_workspace,
                    target=steps_data[-1].get("target", "System"),
                    sequence=task_steps,
                    completion_condition=f"Goal '{raw}' accomplished via AI Task Decomposition"
                )
        except Exception as e:
            print(f"AI Task Decomposition notice ({e}). Falling back to rule-based parser.")

    # Rule-based fallback for multi-step sentences
    delimiters = r'\b(?:and then|and|then|so that|after that)\b'
    sub_cmds = [c.strip() for c in re.split(delimiters, raw_lower) if c and c.strip()]
    seq = []
    for idx, sc in enumerate(sub_cmds, start=1):
        ws = "Desktop"
        act = "EXECUTE"
        if any(sc.startswith(s) for s in OPEN_SYNONYMS):
            act = "OPEN"
            sc = re.sub(r'^(open|launch|start|run|bring up|show)\s+', '', sc).strip()
            ws = sc.title()
        seq.append(TaskStep(idx, ws, act, sc, expected_result=f"Executed '{sc}'"))

    return TaskModel(
        raw_query=raw,
        primary_goal=raw,
        workspace="Desktop",
        target="System",
        sequence=seq,
        completion_condition=f"Goal '{raw}' accomplished"
    )


def build_human_task_model(query: str, current_workspace: str = "UNKNOWN") -> TaskModel:
    """Reads the ENTIRE sentence first to build a human-level TaskModel before execution."""
    raw = query.strip()
    raw_lower = raw.lower()

    # 1. Screenshot Intents
    if any(kw in raw_lower for kw in ["screenshot", "capture screen", "capture window", "save screenshot"]):
        return TaskModel(
            raw_query=raw,
            primary_goal="Take desktop screenshot",
            workspace="Windows",
            target="Screenshot",
            sequence=[
                TaskStep(1, "Windows", "TAKE_SCREENSHOT", "Screen", expected_result="Screenshot captured")
            ],
            completion_condition="Screenshot saved to Pictures"
        )

    # 2. System Settings & Action Intents
    if any(kw in raw_lower for kw in ["bluetooth", "wifi", "network", "night light", "dark mode", "light mode", "battery saver", "hotspot"]):
        return TaskModel(
            raw_query=raw,
            primary_goal=f"Open Windows Setting '{raw}'",
            workspace="Settings",
            target="SystemSetting",
            sequence=[
                TaskStep(1, "Settings", "OPEN_SETTING", raw, expected_result=f"Setting '{raw}' opened")
            ],
            completion_condition=f"Setting '{raw}' active"
        )

    if any(kw in raw_lower for kw in ["lock computer", "lock screen", "sleep", "show desktop", "task view", "action center", "emoji panel"]):
        return TaskModel(
            raw_query=raw,
            primary_goal=f"Execute Windows System Action '{raw}'",
            workspace="Windows",
            target="SystemAction",
            sequence=[
                TaskStep(1, "Windows", "SYSTEM_ACTION", raw, expected_result=f"Action '{raw}' executed")
            ],
            completion_condition=f"Action '{raw}' active"
        )

    # 3. Brightness / Volume Adjustments
    if any(kw in raw_lower for kw in ["brightness", "brighter", "dimmer"]):
        val_match = re.search(r'(\d+)', raw_lower)
        val = int(val_match.group(1)) if val_match else 80
        return TaskModel(
            raw_query=raw,
            primary_goal=f"Set brightness to {val}%",
            workspace="Windows",
            target="Brightness",
            parameters={"value": val},
            sequence=[
                TaskStep(1, "Windows", "INCREASE" if any(w in raw_lower for w in ["increase", "brighter", "up"]) else "SET", "Brightness", {"value": val}, f"Brightness set to {val}%")
            ],
            completion_condition=f"Brightness level is {val}%"
        )

    elif "volume" in raw_lower:
        val_match = re.search(r'(\d+)', raw_lower)
        val = int(val_match.group(1)) if val_match else 40
        return TaskModel(
            raw_query=raw,
            primary_goal=f"Set volume to {val}%",
            workspace="Windows",
            target="Volume",
            parameters={"value": val},
            sequence=[
                TaskStep(1, "Windows", "INCREASE" if any(w in raw_lower for w in ["increase", "up"]) else "SET", "Volume", {"value": val}, f"Volume set to {val}%")
            ],
            completion_condition=f"Volume level is {val}%"
        )

    # 4. Determine Primary Workspace & Context
    workspace = current_workspace
    if "youtube" in raw_lower:
        workspace = "YouTube"
    elif "whatsapp" in raw_lower:
        workspace = "WhatsApp"
    elif "camera" in raw_lower:
        workspace = "Camera"
    elif any(kw in raw_lower for kw in EXPLORER_KEYWORDS) and "google drive" not in raw_lower:
        workspace = "Explorer"
    elif "chrome" in raw_lower:
        workspace = "Chrome"
    elif "edge" in raw_lower:
        workspace = "Edge"
    elif "calculator" in raw_lower or "calc" in raw_lower:
        workspace = "Calculator"

    # 4.5. Calculator Math Intent
    if workspace == "Calculator":
        calc_match = re.search(r'(?:calculate|compute|eval|evaluate|\:)\s*(.*)', raw_lower)
        if calc_match:
            expr = calc_match.group(1).strip()
            expr_clean = expr.replace("times", "*").replace("multiply by", "*").replace("plus", "+").replace("minus", "-").replace("divided by", "/")
            return TaskModel(
                raw_query=raw,
                primary_goal=f"Calculate {expr_clean} inside Calculator",
                workspace="Calculator",
                target="CalculatorApp",
                objects=["display", "keypad"],
                parameters={"expression": expr_clean},
                sequence=[
                    TaskStep(1, "Calculator", "OPEN", "Calculator", expected_result="Calculator active"),
                    TaskStep(2, "Calculator", "TYPE", expr_clean, {"text": expr_clean}, f"Typed '{expr_clean}'"),
                    TaskStep(3, "Calculator", "ENTER", "Calculate", expected_result=f"Calculation completed")
                ],
                dependencies=["Calculator open before entering expression"],
                completion_condition=f"Calculation '{expr_clean}' completed"
            )

    # 5. YouTube Search & Play
    if workspace == "YouTube":
        search_match = re.search(r'search\s+(.*?)\s+(?:and\s+play|and\s+watch|play|watch)', raw_lower)
        if search_match:
            squery = re.sub(r'\b(on youtube|in youtube|youtube)\b', '', search_match.group(1)).strip()
            ordinal_idx, _ = extract_ordinal(raw_lower)
            return TaskModel(
                raw_query=raw,
                primary_goal=f"Play '{squery}' video #{ordinal_idx} on YouTube",
                workspace="YouTube",
                target="video",
                objects=["search_bar", "video_item"],
                parameters={"search_query": squery, "ordinal": ordinal_idx},
                sequence=[
                    TaskStep(1, "YouTube", "OPEN", "YouTube", expected_result="YouTube active"),
                    TaskStep(2, "YouTube", "SEARCH", squery, {"query": squery}, f"Searched '{squery}' in YouTube"),
                    TaskStep(3, "YouTube", "PLAY", "video", {"ordinal": ordinal_idx}, f"Playing video #{ordinal_idx}")
                ],
                dependencies=["Search query entered before play"],
                completion_condition="Target video playing on YouTube"
            )

    # 6. WhatsApp Send Message
    if workspace == "WhatsApp":
        send_match = re.search(r'(?:send\s+(.*?)\s+to\s+(.*)|search\s+(.*?)\s+and\s+send\s+(.*))', raw_lower)
        if send_match:
            g1, g2, g3, g4 = send_match.groups()
            msg, recipient = (g1.strip(), g2.strip()) if (g1 and g2) else (g3.strip(), g4.strip()) if (g3 and g4) else ("Hi", "Mithun")
            return TaskModel(
                raw_query=raw,
                primary_goal=f"Send '{msg}' to {recipient} on WhatsApp",
                workspace="WhatsApp",
                target=recipient,
                objects=["search_bar", "chat_window", "input_box"],
                parameters={"recipient": recipient, "message": msg},
                sequence=[
                    TaskStep(1, "WhatsApp", "OPEN", "WhatsApp", expected_result="WhatsApp active"),
                    TaskStep(2, "WhatsApp", "SEARCH", recipient, {"contact": recipient}, f"Selected contact '{recipient}'"),
                    TaskStep(3, "WhatsApp", "TYPE", msg, {"text": msg}, f"Typed '{msg}' in chat"),
                    TaskStep(4, "WhatsApp", "ENTER", "Send", expected_result="Message sent")
                ],
                dependencies=["Contact selected before typing"],
                completion_condition=f"Message '{msg}' delivered to {recipient}"
            )

    # 7. Camera Record / Photo
    if workspace == "Camera":
        is_rec = "recording" in raw_lower or "record" in raw_lower
        return TaskModel(
            raw_query=raw,
            primary_goal="Record video in Camera" if is_rec else "Take photo in Camera",
            workspace="Camera",
            target="Video" if is_rec else "Photo",
            objects=["shutter_button"],
            sequence=[
                TaskStep(1, "Camera", "OPEN", "Camera", expected_result="Camera active"),
                TaskStep(2, "Camera", "START_RECORDING" if is_rec else "TAKE_PHOTO", "Shutter", expected_result="Action recorded")
            ],
            completion_condition="Camera recording active" if is_rec else "Photo captured"
        )

    # 8. Explorer Navigation & Open Item (ONLY when Explorer is explicitly targetted)
    if workspace == "Explorer" and any(kw in raw_lower for kw in ["open file", "open image", "open item", "select file", "select item", "navigate"]):
        dest = "D:\\" if ("disk d" in raw_lower or "drive d" in raw_lower) else "Downloads" if "downloads" in raw_lower else "C:\\"
        ordinal_idx, _ = extract_ordinal(raw_lower)
        return TaskModel(
            raw_query=raw,
            primary_goal=f"Open item #{ordinal_idx} in {dest}",
            workspace="Explorer",
            target=dest,
            parameters={"destination": dest, "ordinal": ordinal_idx},
            sequence=[
                TaskStep(1, "Explorer", "OPEN", "Explorer", expected_result="Explorer active"),
                TaskStep(2, "Explorer", "GO", dest, {"path": dest}, f"Navigated to {dest}"),
                TaskStep(3, "Explorer", "SELECT", "item", {"ordinal": ordinal_idx}, f"Selected item #{ordinal_idx}"),
                TaskStep(4, "Explorer", "OPEN", "item", {"ordinal": ordinal_idx}, f"Opened item #{ordinal_idx}")
            ],
            completion_condition=f"Item #{ordinal_idx} opened in {dest}"
        )

    # 9. Multi-step Natural Speech AI Decomposition
    if any(kw in raw_lower for kw in [" and ", " then ", " to ", " so that ", " after that "]):
        ai_model = decompose_speech_with_ai(raw, workspace)
        if ai_model and ai_model.sequence:
            return ai_model

    # 10. Application Open / Launch Synonyms
    for syn in OPEN_SYNONYMS:
        if raw_lower.startswith(f"{syn} "):
            app = raw_lower.replace(f"{syn} ", "").strip()
            return TaskModel(
                raw_query=raw,
                primary_goal=f"Open application {app}",
                workspace=app,
                target=app,
                sequence=[
                    TaskStep(1, app, "OPEN", app, expected_result=f"{app} active")
                ],
                completion_condition=f"{app} opened"
            )

    # 11. Application Close / Exit Synonyms
    for syn in CLOSE_SYNONYMS:
        if raw_lower.startswith(f"{syn} "):
            app = raw_lower.replace(f"{syn} ", "").strip()
            return TaskModel(
                raw_query=raw,
                primary_goal=f"Close application {app}",
                workspace=app,
                target=app,
                sequence=[
                    TaskStep(1, app, "CLOSE", app, expected_result=f"{app} closed")
                ],
                completion_condition=f"{app} closed"
            )

    # 12. Universal AI Fallback
    return decompose_speech_with_ai(raw, workspace)
