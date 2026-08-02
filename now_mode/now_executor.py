import re
import time
import pyautogui
import win32gui
from typing import Dict, Any
from now_mode.uia_inspector import UIAInspector
from now_mode.visual_search_hud import show_live_search_widget

pyautogui.FAILSAFE = False

class NowExecutor:
    """Truly Universal Now Executor: Operates STRICTLY on the CURRENT active page/window on screen."""

    def __init__(self):
        self.uia_inspector = UIAInspector()

    def execute_resolved_target(self, resolved: Dict[str, Any]) -> bool:
        if not resolved or not isinstance(resolved, dict):
            return False

        action_type = str(resolved.get("type", "CLICK")).upper()
        target_name = str(resolved.get("target", "UI Element")).strip()
        target_lower = target_name.lower()

        # Safely parse ordinal
        raw_ordinal = resolved.get("ordinal")
        try:
            ordinal = int(raw_ordinal) if raw_ordinal is not None else 1
        except (ValueError, TypeError):
            ordinal = 1

        print(f"[NowExecutor]: Executing Action '{action_type}' for target '{target_name}'")

        try:
            hwnd = win32gui.GetForegroundWindow()
            title = win32gui.GetWindowText(hwnd).lower()

            # 1. Restart Video from Beginning (Key 0)
            if action_type == "RESTART_VIDEO":
                print("[NowExecutor YouTube]: Restarting video from 0:00 (Key '0')...")
                pyautogui.press('0')
                time.sleep(0.15)
                pyautogui.press('k')  # Ensure video plays if paused
                time.sleep(0.3)
                return True

            # 2. Seek Video to Specific Minute
            elif action_type == "SEEK_VIDEO":
                min_val = resolved.get("minute", 1)
                try:
                    min_num = int(min_val)
                except (ValueError, TypeError):
                    min_num = 1
                key_str = str(min_num) if 0 <= min_num <= 9 else '1'
                print(f"[NowExecutor YouTube]: Seeking video to minute mark '{min_num}' (Key '{key_str}')...")
                pyautogui.press(key_str)
                time.sleep(0.3)
                return True

            # 3. Toggle Playback (Resume, Pause, Stop, Play)
            elif action_type in ["TOGGLE_PLAYBACK", "PLAY_VIDEO"]:
                print("[NowExecutor YouTube]: Toggling video play/pause state...")
                if "youtube" in title or "video" in title:
                    pyautogui.press('k')
                else:
                    pyautogui.press('space')
                time.sleep(0.3)
                return True

            # 4. Refresh Page
            elif action_type == "REFRESH_PAGE":
                print("[NowExecutor]: Refreshing current page...")
                pyautogui.press('f5')
                time.sleep(0.3)
                return True

            # 5. Play Nth Video on Current Screen
            elif action_type == "PLAY_NTH_VIDEO":
                coords = resolved.get("coords")
                if coords and isinstance(coords, (list, tuple)) and len(coords) >= 2 and coords[0] > 0 and coords[1] > 0:
                    print(f"[NowExecutor Screen Grid]: Clicking Video #{ordinal} at screen coordinates ({coords[0]}, {coords[1]})")
                    pyautogui.click(int(coords[0]), int(coords[1]))
                else:
                    print(f"[NowExecutor Tab Focus]: Navigating to Video #{ordinal} on current screen...")
                    pyautogui.press('home')
                    time.sleep(0.15)
                    for _ in range(max(1, ordinal * 2)):
                        pyautogui.press('tab')
                        time.sleep(0.08)
                    pyautogui.press('enter')
                time.sleep(0.3)
                return True

            # 6. TRULY UNIVERSAL SEARCH & CHOOSE (Current Page & Window ONLY)
            elif action_type in ["CLICK", "CLICK_ICON"]:
                clean_text = re.sub(r'\b(button|link|icon|tab)\b', '', target_lower, flags=re.IGNORECASE).strip()
                if not clean_text:
                    clean_text = target_name

                print(f"[NOW MODE Truly Universal Search]: Searching active window '{title}' for '{clean_text}'...")
                show_live_search_widget(clean_text, duration=1.5)

                # Step 1: Programmatic UIA Invocation on active window elements
                if self.uia_inspector.invoke_element_by_name(hwnd, target_name):
                    print(f"[NOW MODE Universal UIA Direct Action]: Successfully clicked '{clean_text}' programmatically on current window.")
                    return True

                # Step 2: Exact Coordinate Resolution & Click on active window
                coords = resolved.get("coords")
                if not coords:
                    try:
                        coords = self.uia_inspector.find_element_center_by_name(hwnd, target_name)
                    except Exception:
                        pass

                if coords and isinstance(coords, (list, tuple)) and len(coords) >= 2 and coords[0] > 0 and coords[1] > 0:
                    cx, cy = int(coords[0]), int(coords[1])
                    print(f"[NOW MODE Universal Direct Click]: Clicking matched '{clean_text}' at screen position ({cx}, {cy})...")
                    pyautogui.click(cx, cy)
                    time.sleep(0.3)
                    return True

                # Step 3: Browser In-Page Fallback (Ctrl+F for in-page web DOM elements)
                is_browser = any(b in title for b in ["chrome", "edge", "firefox", "brave", "opera", "browser"])
                if is_browser:
                    print(f"[NOW MODE Universal Browser Fallback]: Searching current webpage for '{clean_text}' via Ctrl+F...")
                    pyautogui.hotkey('ctrl', 'f')
                    time.sleep(0.15)
                    pyautogui.write(clean_text, interval=0.04)
                    time.sleep(0.15)
                    pyautogui.press('enter')
                    time.sleep(0.15)
                    pyautogui.press('escape')
                    time.sleep(0.15)
                    pyautogui.press('enter')
                    time.sleep(0.3)
                    return True

                print(f"[NOW MODE Universal Search Notice]: Target element '{clean_text}' was not found on active window.")
                return False

            # 7. Scroll Commands
            elif action_type == "SCROLL":
                direction = str(resolved.get("direction", "down")).lower()
                amount = -800 if direction == "down" else 800
                pyautogui.scroll(amount)
                time.sleep(0.2)
                return True

            # 8. Search Input
            elif action_type == "SEARCH":
                query = str(resolved.get("query", resolved.get("target", ""))).strip()
                if query:
                    pyautogui.press('/')
                    time.sleep(0.15)
                    pyautogui.hotkey('ctrl', 'a')
                    pyautogui.write(query, interval=0.04)
                    pyautogui.press('enter')
                    time.sleep(0.5)
                return True

            # 9. Type Input
            elif action_type == "TYPE":
                text_to_type = str(resolved.get("query", resolved.get("target", ""))).strip()
                if text_to_type:
                    pyautogui.write(text_to_type, interval=0.04)
                    time.sleep(0.2)
                return True

            # 10. Key Shortcut
            elif action_type == "KEY":
                shortcut = str(resolved.get("shortcut", "enter")).lower()
                pyautogui.press(shortcut)
                time.sleep(0.2)
                return True

        except Exception as e:
            print(f"[NowExecutor notice]: {e}")

        return True
