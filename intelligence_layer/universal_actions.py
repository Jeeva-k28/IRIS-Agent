UNIVERSAL_ACTIONS = {
    "OPEN": "Launches or brings target application/workspace to foreground",
    "CLOSE": "Closes active window, tab, or target application",
    "SEARCH": "Executes search query within current active workspace",
    "GO": "Navigates to specified location, folder, URL, or drive",
    "BACK": "Navigates backward in history or hierarchy",
    "FORWARD": "Navigates forward in history or hierarchy",
    "CLICK": "Clicks specified element, button, or target",
    "SELECT": "Selects specified item, option, or text",
    "TYPE": "Types text smoothly at active input field",
    "ENTER": "Presses Enter key to confirm action",
    "SCROLL": "Scrolls active workspace view up or down",
    "PLAY": "Plays media playback or Nth item",
    "PAUSE": "Pauses current media playback",
    "RESUME": "Resumes current media playback",
    "STOP": "Stops playback or running process",
    "INCREASE": "Increases system/app parameter (e.g. Volume, Brightness)",
    "DECREASE": "Decreases system/app parameter (e.g. Volume, Brightness)",
    "TURN_ON": "Activates setting or feature mode",
    "TURN_OFF": "Deactivates setting or feature mode",
    "CREATE": "Creates new file, folder, chat, or item",
    "DELETE": "Deletes specified file, message, or item",
    "RENAME": "Renames specified file or folder",
    "MOVE": "Moves item to specified location",
    "COPY": "Copies selected content to clipboard",
    "PASTE": "Pastes clipboard content into active target",
    "UPLOAD": "Uploads specified file to workspace",
    "DOWNLOAD": "Downloads specified item or file",
    "SAVE": "Saves active document or media",
    "PRINT": "Triggers print dialog for active document",
    "SHARE": "Opens share dialog for current content",
    "ATTACH": "Attaches file to message or email",
    "REPLY": "Replies to selected message or email",
    "REFRESH": "Reloads or refreshes current page or workspace view"
}

def is_universal_action(action_name: str) -> bool:
    """Returns True if the action is one of the 35 Universal Actions."""
    return action_name.upper() in UNIVERSAL_ACTIONS
