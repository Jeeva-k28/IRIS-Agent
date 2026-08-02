import tkinter as tk
import threading
import time

_current_root = None

def show_live_search_widget(target_text: str, duration: float = 1.4):
    """Renders Chrome-style Live Search Widget in top-right corner with live character typing animation and white box selection match highlight."""

    def run_widget():
        global _current_root
        try:
            root = tk.Tk()
            _current_root = root
            root.title("IRIS Live Search")
            root.attributes("-topmost", True)
            root.overrideredirect(True)
            root.configure(bg="#181C1E")

            screen_w = root.winfo_screenwidth()
            hud_w, hud_h = 320, 40
            hud_x = max(10, screen_w - hud_w - 40)
            hud_y = 45
            root.geometry(f"{hud_w}x{hud_h}+{hud_x}+{hud_y}")

            # Outer rounded border container
            container = tk.Frame(root, bg="#1F2327", bd=1, relief="solid", highlightbackground="#363C42", highlightthickness=1)
            container.pack(fill="both", expand=True)

            # Typing Text Display (Left)
            lbl_type = tk.Label(container, text="", font=("Consolas", 11, "bold"), fg="#E6EFE9", bg="#1F2327", anchor="w")
            lbl_type.pack(side="left", padx=(12, 5))

            # Controls & Match Count (Right)
            lbl_close = tk.Label(container, text="✕", font=("Segoe UI", 10), fg="#8A95A5", bg="#1F2327")
            lbl_close.pack(side="right", padx=(2, 10))

            lbl_down = tk.Label(container, text="˅", font=("Segoe UI", 11, "bold"), fg="#8A95A5", bg="#1F2327")
            lbl_down.pack(side="right", padx=3)

            lbl_up = tk.Label(container, text="˄", font=("Segoe UI", 11, "bold"), fg="#8A95A5", bg="#1F2327")
            lbl_up.pack(side="right", padx=3)

            lbl_div = tk.Label(container, text="|", font=("Segoe UI", 11), fg="#3E444B", bg="#1F2327")
            lbl_div.pack(side="right", padx=4)

            lbl_match = tk.Label(container, text="", font=("Consolas", 10, "bold"), fg="#11111B", bg="#1F2327", padx=4, pady=1)
            lbl_match.pack(side="right", padx=4)

            root.update()

            # Character-by-character live typing animation
            clean = target_text.strip()
            typed = ""
            for char in clean:
                typed += char
                lbl_type.configure(text=typed)
                root.update()
                time.sleep(0.03)

            # Highlight 1/1 with sleek white selection box after typing finishes completely
            time.sleep(0.08)
            lbl_match.configure(text="1/1", bg="#FFFFFF", fg="#11111B")
            container.configure(highlightbackground="#FFFFFF", highlightthickness=2)
            root.update()

            time.sleep(duration)
            root.destroy()
            _current_root = None
        except Exception:
            _current_root = None

    t = threading.Thread(target=run_widget, daemon=True)
    t.start()
    # Calculate typing duration so NowExecutor waits until typing finishes completely before clicking!
    typing_delay = len(target_text.strip()) * 0.03 + 0.15
    time.sleep(typing_delay)
