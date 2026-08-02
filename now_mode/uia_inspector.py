import re
import win32gui
from typing import Optional, Tuple

try:
    import comtypes.client
    comtypes.CoInitialize()
    UIAutomationClient = comtypes.client.GetModule('UIAutomationCore.dll')
    UIA_ENGINE = comtypes.client.CreateObject(UIAutomationClient.CUIAutomation, interface=UIAutomationClient.IUIAutomation)
except Exception as e:
    UIA_ENGINE = None
    UIAutomationClient = None

# UIA Pattern IDs
UIA_InvokePatternId = 10000
UIA_SelectionItemPatternId = 10010
UIA_TogglePatternId = 10015

class UIAInspector:
    """Native Windows UI Automation Inspector with Parent Card Resolution, Programmatic Invocation & Exact Interactive Matching."""

    def __init__(self):
        pass

    def invoke_element_by_name(self, hwnd: int, target_name: str) -> bool:
        """Attempts direct programmatic invocation (Invoke/Select/Toggle) on element or parent card container without moving mouse cursor."""
        if not hwnd or not target_name or not UIA_ENGINE or not UIAutomationClient:
            return False

        target_l = target_name.strip().lower()
        clean_target = re.sub(r'\b(button|link|icon|tab|option|card)\b', '', target_l, flags=re.IGNORECASE).strip()
        if not clean_target:
            clean_target = target_l

        try:
            comtypes.CoInitialize()
            root = UIA_ENGINE.ElementFromHandle(hwnd)
            if not root:
                return False

            condition = UIA_ENGINE.CreateTrueCondition()
            elements = root.FindAll(UIAutomationClient.TreeScope_Subtree, condition)
            if not elements:
                return False

            n_elems = elements.Length
            target_el = None

            # Search for Exact Name or Substring Match
            for i in range(n_elems):
                try:
                    el = elements.GetElement(i)
                    name = (el.CurrentName or "").strip().lower()
                    if clean_target == name or (len(clean_target) >= 3 and clean_target in name):
                        target_el = el
                        if clean_target == name:
                            break  # Exact match priority
                except Exception:
                    pass

            if target_el:
                curr = target_el
                # Check element itself and up to 3 parent levels (for cards/containers like Apple Devices card)
                for level in range(3):
                    if not curr:
                        break

                    # Try InvokePattern
                    try:
                        p_unk = curr.GetCurrentPattern(UIA_InvokePatternId)
                        if p_unk:
                            p_invoke = p_unk.QueryInterface(UIAutomationClient.IUIAutomationInvokePattern)
                            p_invoke.Invoke()
                            print(f"[Programmatic UIA Invoke]: Successfully invoked '{clean_target}' (level {level}) directly.")
                            return True
                    except Exception:
                        pass

                    # Try SelectionItemPattern
                    try:
                        p_unk = curr.GetCurrentPattern(UIA_SelectionItemPatternId)
                        if p_unk:
                            p_select = p_unk.QueryInterface(UIAutomationClient.IUIAutomationSelectionItemPattern)
                            p_select.Select()
                            print(f"[Programmatic UIA Select]: Successfully selected '{clean_target}' (level {level}) directly.")
                            return True
                    except Exception:
                        pass

                    # Try TogglePattern
                    try:
                        p_unk = curr.GetCurrentPattern(UIA_TogglePatternId)
                        if p_unk:
                            p_toggle = p_unk.QueryInterface(UIAutomationClient.IUIAutomationTogglePattern)
                            p_toggle.Toggle()
                            print(f"[Programmatic UIA Toggle]: Successfully toggled '{clean_target}' (level {level}) directly.")
                            return True
                    except Exception:
                        pass

                    # Climb up to parent container element
                    try:
                        walker = UIA_ENGINE.ControlViewWalker
                        curr = walker.GetParentElement(curr)
                    except Exception:
                        break

        except Exception as e:
            print(f"[UIAInspector Invoke notice]: {e}")

        return False

    def find_element_center_by_name(self, hwnd: int, target_name: str) -> Optional[Tuple[int, int]]:
        """Scans active window UI Automation tree for elements or card containers matching target_name and returns (cx, cy)."""
        if not hwnd or not target_name:
            return None

        target_l = target_name.strip().lower()
        clean_target = re.sub(r'\b(button|link|icon|tab|option|card)\b', '', target_l, flags=re.IGNORECASE).strip()
        if not clean_target:
            clean_target = target_l

        kw_words = set(clean_target.split())

        # 1. Native Windows IUIAutomation COM Scanning
        if UIA_ENGINE and UIAutomationClient:
            try:
                comtypes.CoInitialize()
                root = UIA_ENGINE.ElementFromHandle(hwnd)
                if root:
                    condition = UIA_ENGINE.CreateTrueCondition()
                    elements = root.FindAll(UIAutomationClient.TreeScope_Subtree, condition)

                    if elements:
                        n_elems = elements.Length
                        exact_match = None
                        substring_match = None
                        token_match = None

                        for i in range(n_elems):
                            try:
                                el = elements.GetElement(i)
                                name = (el.CurrentName or "").strip().lower()
                                help_txt = (el.CurrentHelpText or "").strip().lower()
                                aria_lbl = (el.CurrentAriaProperties or "").strip().lower()

                                combined_txt = f"{name} {help_txt} {aria_lbl}".strip()
                                if not combined_txt:
                                    continue

                                rect = el.CurrentBoundingRectangle
                                w = rect.right - rect.left
                                h = rect.bottom - rect.top

                                if w > 4 and h > 4:
                                    cx = rect.left + w // 2
                                    cy = rect.top + h // 2

                                    # Priority 1: Exact name match
                                    if clean_target == name or clean_target == combined_txt:
                                        print(f"[Native IUIAutomation Exact Match]: Found control '{name}' at position ({cx}, {cy})")
                                        return (cx, cy)

                                    # Priority 2: Substring match (e.g. "apple devices" in card title)
                                    if not substring_match and (clean_target in name or (len(clean_target) >= 3 and name in clean_target)):
                                        substring_match = (cx, cy, name)

                                    # Priority 3: Word token match
                                    txt_words = set(name.split())
                                    if not token_match and kw_words and (kw_words.issubset(txt_words) or txt_words.issubset(kw_words)):
                                        token_match = (cx, cy, name)

                            except Exception:
                                pass

                        if substring_match:
                            print(f"[Native IUIAutomation Substring Match]: Found control '{substring_match[2]}' at position ({substring_match[0]}, {substring_match[1]})")
                            return (substring_match[0], substring_match[1])

                        if token_match:
                            print(f"[Native IUIAutomation Token Match]: Found control '{token_match[2]}' at position ({token_match[0]}, {token_match[1]})")
                            return (token_match[0], token_match[1])

            except Exception as e:
                print(f"[UIAInspector COM notice]: {e}")

        # 2. Legacy EnumChildWindows Fallback
        matched_coords = []

        def enum_child_proc(child_hwnd, param):
            try:
                if win32gui.IsWindowVisible(child_hwnd):
                    text = win32gui.GetWindowText(child_hwnd).strip().lower()
                    if text and (clean_target in text or text in clean_target):
                        rect = win32gui.GetWindowRect(child_hwnd)
                        cw = rect[2] - rect[0]
                        ch = rect[3] - rect[1]
                        if cw > 5 and ch > 5:
                            cx = rect[0] + cw // 2
                            cy = rect[1] + ch // 2
                            matched_coords.append((cx, cy))
            except Exception:
                pass
            return True

        try:
            win32gui.EnumChildWindows(hwnd, enum_child_proc, None)
            if matched_coords:
                print(f"[Legacy UIAInspector]: Found control '{clean_target}' in desktop app at screen position {matched_coords[0]}")
                return matched_coords[0]
        except Exception:
            pass

        return None
