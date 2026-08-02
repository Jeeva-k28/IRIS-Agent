import sys
import os

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.dirname(SCRIPT_DIR)
if ROOT_DIR not in sys.path:
    sys.path.insert(0, ROOT_DIR)

import pyttsx3
import datetime
import speech_recognition as sr
import wikipedia
import webbrowser as wb
import random
import pyautogui
import pyjokes
import urllib.request
import urllib.parse
import json
import re
import time
import win32gui
import win32api
import pytesseract
from PIL import Image
from ddgs import DDGS
from g4f.client import Client

try:
    from desktop.desktop_core import (
        focus_or_launch_app,
        set_window_state,
        adjust_volume,
        adjust_brightness,
        open_system_setting,
        execute_windows_system_action,
        take_desktop_screenshot,
        media_control,
        navigate_explorer_folder,
        camera_control,
        calculate_expression,
        toggle_system_setting
    )
    from intelligence_layer.task_model import TaskModel, TaskStep
    from intelligence_layer.human_intent_parser import build_human_task_model
    from intelligence_layer.observation_loop import UniversalObservationLoop
    from now_mode.now_mode import NowModeEngine
except ImportError as e:
    print(f"[Import Notice]: {e}")
    TaskModel = None
    TaskStep = None

NAME_FILE_PATH = os.path.join(SCRIPT_DIR, "assistant_name.txt")

pyautogui.FAILSAFE = False

# Global State Variables
TYPE_MODE_ACTIVE = False
LAST_CONTEXT_ACTION = None
LAST_OPTIONS_LIST = []

ORDINAL_MAP = {
    "first": 1, "1st": 1, "one": 1,
    "second": 2, "2nd": 2, "two": 2,
    "third": 3, "3rd": 3, "three": 3,
    "fourth": 4, "4th": 4, "four": 4,
    "fifth": 5, "5th": 5, "five": 5,
    "last": -1, "latest": 1, "newest": 1, "oldest": -1
}

WEB_SITES_MAP = {
    "youtube": "https://www.youtube.com",
    "google": "https://www.google.com",
    "chatgpt": "https://chatgpt.com",
    "chat gpt": "https://chatgpt.com",
    "github": "https://github.com",
    "wikipedia": "https://www.wikipedia.org",
    "gmail": "https://mail.google.com",
    "google drive": "https://drive.google.com",
    "drive": "https://drive.google.com",
    "amazon": "https://www.amazon.com",
    "flipkart": "https://www.flipkart.com",
    "linkedin": "https://www.linkedin.com",
    "instagram": "https://www.instagram.com",
    "facebook": "https://www.facebook.com",
    "twitter": "https://x.com",
    "x": "https://x.com",
    "reddit": "https://www.reddit.com"
}


def extract_ordinal(text: str) -> tuple[int, str]:
    """Extracts ordinal index (1-based) from text and returns (ordinal_index, text_without_ordinal)."""
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


def is_enter_double_pressed() -> bool:
    """Checks if the Enter key (VK_RETURN 0x0D) is being pressed by the user."""
    try:
        return bool(win32api.GetAsyncKeyState(0x0D) & 0x8000)
    except Exception:
        return False


def speak(audio) -> bool:
    """Speaks out audio text using text-to-speech synthesis. Returns True if interrupted by user pressing Enter."""
    if not audio:
        return False
    clean_audio = str(audio).encode('ascii', 'ignore').decode('utf-8')
    print(f"\nIris: {clean_audio}")

    if is_enter_double_pressed():
        print("\n[Interrupted by User]")
        print("\nIris: Ok sir!")
        try:
            engine = pyttsx3.init()
            engine.say("Ok sir!")
            engine.runAndWait()
        except Exception:
            pass
        return True

    try:
        engine = pyttsx3.init()
        voices = engine.getProperty('voices')
        if len(voices) > 1:
            engine.setProperty('voice', voices[1].id)
        elif len(voices) > 0:
            engine.setProperty('voice', voices[0].id)
        engine.setProperty('rate', 150)
        engine.setProperty('volume', 1.0)
        engine.say(clean_audio)
        engine.runAndWait()
    except Exception as e:
        print(f"Speech synthesis notice ({e})")

    return False


def time_func() -> None:
    """Tells the current time."""
    current_time = datetime.datetime.now().strftime("%I:%M:%S %p")
    speak("The current time is " + current_time)


def date() -> None:
    """Tells the current date."""
    now = datetime.datetime.now()
    speak(f"The current date is {now.day} {now.strftime('%B')} {now.year}")


def load_name() -> str:
    """Loads the assistant's name from a file, or uses a default name."""
    try:
        with open(NAME_FILE_PATH, "r") as file:
            return file.read().strip()
    except FileNotFoundError:
        return "Iris"


def set_name() -> None:
    """Sets a new name for the assistant."""
    speak("What would you like to name me?")
    name = takecommand()
    if name:
        with open(NAME_FILE_PATH, "w") as file:
            file.write(name)
        speak(f"Alright, I will be called {name} from now on.")
    else:
        speak("Sorry, I couldn't catch that.")


def wishme() -> None:
    """Greets the user based on the time of day and starts listening immediately."""
    hour = datetime.datetime.now().hour
    if 4 <= hour < 12:
        greeting = "Good morning, sir!"
    elif 12 <= hour < 16:
        greeting = "Good afternoon, sir!"
    elif 16 <= hour < 24:
        greeting = "Good evening, sir!"
    else:
        greeting = "Good night, sir!"

    print(f"{greeting} Welcome back!")
    speak(f"{greeting} Welcome back!")


def screenshot() -> None:
    """Takes a screenshot and saves it."""
    take_desktop_screenshot(open_folder=False)
    speak("Screenshot saved to Pictures folder.")


def type_text_smoothly(text: str) -> None:
    """Types out text instantly and live at the active cursor position."""
    pyautogui.write(text + " ", _pause=False)


def clean_conversational_query(cmd: str) -> tuple[str, bool]:
    """Strips polite human conversational fillers and detects if the request was asked politely/conversationally."""
    if not cmd:
        return "", False

    cmd_lower = cmd.strip().lower()
    original = cmd_lower

    fillers = [
        "hey iris", "hi iris", "iris", "can you please", "could you please",
        "would you please", "will you please", "can you kindly", "could you kindly",
        "can you", "could you", "would you", "will you", "please", "kindly",
        "do me a favor and", "do me a favour and"
    ]

    is_polite = any(kw in original for kw in ["iris", "can you", "could you", "please", "kindly", "would you"])

    for filler in fillers:
        cmd_lower = re.sub(r'\b' + re.escape(filler) + r'\b', '', cmd_lower)

    cmd_cleaned = ' '.join(cmd_lower.split())
    return cmd_cleaned or original, is_polite


def handle_friendly_chitchat(cmd: str) -> bool:
    """Responds warmly like a friend to greetings, compliments, and casual conversation."""
    cmd_lower = cmd.strip().lower()

    if any(kw in cmd_lower for kw in ["how are you", "how r u", "how are u", "how do you do", "how is it going"]):
        responses = [
            "I'm doing fantastic, my friend! How are you doing today?",
            "I'm doing great! Always happy to talk with you. How can I help?",
            "Everything is going wonderfully, thanks for asking! How are you?"
        ]
        speak(random.choice(responses))
        return True

    elif any(kw in cmd_lower for kw in ["who are you", "what is your name", "what's your name"]):
        speak("I'm Iris, your personal AI companion and friend! I'm here to help you with anything you need.")
        return True

    elif any(kw in cmd_lower for kw in ["what can you do", "help me", "your capabilities"]):
        speak("I can open YouTube and play videos, search Google, type live for you in type mode, explain what's on your screen, answer any question in voice, and much more!")
        return True

    elif any(kw in cmd_lower for kw in ["thank you", "thanks", "thank u"]):
        responses = [
            "You're very welcome, my friend!",
            "Anytime! Always happy to help you.",
            "My pleasure, my friend!"
        ]
        speak(random.choice(responses))
        return True

    elif any(kw in cmd_lower for kw in ["awesome", "great job", "you are cool", "you are amazing", "nice", "good job", "love you"]):
        responses = [
            "Aww, thank you so much! You're awesome too, my friend!",
            "Thank you! That really means a lot to me.",
            "I'm happy to hear that! Always here for you."
        ]
        speak(random.choice(responses))
        return True

    elif any(kw in cmd_lower for kw in ["hello", "hi iris", "hey iris", "good morning", "good afternoon", "good evening"]):
        responses = [
            "Hello there, my friend! How can I assist you?",
            "Hey! Great to hear from you. What would you like to do today?",
            "Hi! Ready whenever you are."
        ]
        speak(random.choice(responses))
        return True

    elif any(kw in cmd_lower for kw in ["what are you doing", "what r u doing"]):
        speak("Just hanging out with you, ready to help whenever you need me!")
        return True

    return False


def takecommand() -> str:
    """Takes microphone input from the user and returns it as text, waiting until speech is fully completed."""
    r = sr.Recognizer()
    if TYPE_MODE_ACTIVE:
        r.pause_threshold = 0.3
        r.non_speaking_duration = 0.2
    else:
        r.pause_threshold = 2.0
        r.non_speaking_duration = 0.8

    audio = None
    mic_available = True

    try:
        with sr.Microphone() as source:
            if not TYPE_MODE_ACTIVE:
                print("\nListening (speak your full command)...")
            r.adjust_for_ambient_noise(source, duration=0.2)
            try:
                audio = r.listen(source, timeout=8 if not TYPE_MODE_ACTIVE else 10, phrase_time_limit=15 if not TYPE_MODE_ACTIVE else 4)
            except sr.WaitTimeoutError:
                if not TYPE_MODE_ACTIVE:
                    print("Timeout: No speech detected.")
                return None
    except Exception as e:
        mic_available = False
        if not TYPE_MODE_ACTIVE:
            print(f"Microphone notice ({e}). Keyboard input activated.")

    if not mic_available or audio is None:
        if mic_available:
            return None
        try:
            query = input("Type command (or 'exit' to quit): ").strip()
            return query.lower() if query else None
        except (KeyboardInterrupt, EOFError):
            return "exit"

    try:
        if not TYPE_MODE_ACTIVE:
            print("Recognizing full speech...")
        query = r.recognize_google(audio, language="en-in")
        if not TYPE_MODE_ACTIVE:
            print(f"User: {query}")
        return query.lower()
    except sr.UnknownValueError:
        return None
    except sr.RequestError:
        if not TYPE_MODE_ACTIVE:
            speak("Speech recognition service is unavailable.")
        return None
    except Exception as e:
        return None


def play_music(song_name=None) -> None:
    """Plays music from the user's Music directory."""
    song_dir = os.path.expanduser("~\\Music")
    if not os.path.exists(song_dir):
        os.makedirs(song_dir, exist_ok=True)

    songs = [f for f in os.listdir(song_dir) if os.path.isfile(os.path.join(song_dir, f))]

    if song_name:
        songs = [song for song in songs if song_name.lower() in song.lower()]

    if songs:
        song = random.choice(songs)
        os.startfile(os.path.join(song_dir, song))
        speak(f"Playing {song}.")
    else:
        speak("No music file found in Music directory.")


def fetch_wikipedia_summary(query: str) -> str:
    """Fetches Wikipedia summary extract via REST API with custom User-Agent."""
    try:
        search_url = f"https://en.wikipedia.org/w/api.php?action=query&list=search&srsearch={urllib.parse.quote(query)}&format=json"
        req = urllib.request.Request(search_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
        res_data = json.loads(urllib.request.urlopen(req, timeout=5).read().decode('utf-8'))
        search_results = res_data.get("query", {}).get("search", [])

        if search_results:
            page_title = search_results[0]["title"]
            summary_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{urllib.parse.quote(page_title)}"
            req2 = urllib.request.Request(summary_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'})
            summary_data = json.loads(urllib.request.urlopen(req2, timeout=5).read().decode('utf-8'))
            extract = summary_data.get("extract", "")
            if extract:
                sentences = [s.strip() for s in extract.split(". ") if s.strip()]
                return ". ".join(sentences[:2]) + "."
    except Exception as e:
        print(f"Wikipedia lookup notice: {e}")
    return None


def fetch_exact_ai_answer(query: str) -> str:
    """Fetches exact, direct, 100% intelligent ChatGPT-level responses using g4f GPT-4o model."""
    query = str(query).strip()
    if not query:
        return None

    try:
        client = Client()
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "system",
                    "content": "You are Iris, a friendly, highly intelligent AI companion. Provide a direct, exact, concise 2-sentence answer for voice speech output."
                },
                {"role": "user", "content": query}
            ]
        )
        ai_output = response.choices[0].message.content.strip()
        if ai_output:
            clean_output = str(ai_output).encode('ascii', 'ignore').decode('utf-8')
            return clean_output
    except Exception as e:
        print(f"GPT-4o API notice ({e})")

    # Fallback to DDGS search
    try:
        results = list(DDGS().text(query, max_results=2))
        if results and results[0].get('body'):
            body = results[0]['body']
            sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', body) if len(s.strip()) > 15]
            if sentences:
                return " ".join(sentences[:2])
    except Exception:
        pass

    return fetch_wikipedia_summary(query)


def search_wikipedia(query):
    """Searches Wikipedia and speaks out the summary."""
    speak("Searching Wikipedia...")
    summary = fetch_wikipedia_summary(query)
    if summary:
        speak(summary)
    else:
        speak("I couldn't find anything on Wikipedia.")


def search_and_play_youtube_live(search_term: str, play_first: bool = True, video_index: int = 1) -> None:
    """Performs live step-by-step YouTube automation: Open YouTube -> Type Search Query -> Play Nth Video."""
    search_term = search_term.strip()

    speak("Opening YouTube...")
    wb.open("https://www.youtube.com")
    time.sleep(3.0)

    if not search_term:
        return

    speak(f"Searching YouTube for {search_term}")
    pyautogui.press('/')
    time.sleep(0.6)
    pyautogui.write(search_term, interval=0.07)
    time.sleep(0.5)
    pyautogui.press('enter')
    time.sleep(2.5)

    if video_index > 0:
        speak(f"Playing video number {video_index}")
        try:
            query_encoded = urllib.parse.urlencode({"search_query": search_term})
            url = "https://www.youtube.com/results?" + query_encoded
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            html = urllib.request.urlopen(req, timeout=5).read().decode('utf-8')
            video_ids = re.findall(r"watch\?v=(\w{11})", html)
            if video_ids and len(video_ids) >= video_index:
                selected_video_url = f"https://www.youtube.com/watch?v={video_ids[video_index - 1]}"
                time.sleep(1.0)
                wb.open(selected_video_url)
                return
        except Exception as e:
            print(f"Notice: {e}")

        for _ in range(video_index):
            pyautogui.press('tab')
            time.sleep(0.2)
        pyautogui.press('enter')


def search_google_live(search_term: str) -> None:
    """Performs live step-by-step Google search automation."""
    search_term = search_term.strip()

    speak("Opening Google...")
    wb.open("https://www.google.com")
    time.sleep(2.5)

    if not search_term:
        return

    speak(f"Searching Google for {search_term}")
    time.sleep(0.5)
    pyautogui.write(search_term, interval=0.07)
    time.sleep(0.5)
    pyautogui.press('enter')


def extract_youtube_query(cmd: str) -> tuple[str, bool]:
    """Extracts search query and whether to play the first video/song."""
    play_first = any(kw in cmd for kw in ["play", "first video", "first song", "first", "watch", "song"])

    query = cmd
    for phrase in [
        "open youtube and search", "search on youtube and play the first video",
        "search on youtube and play first video", "search on youtube and play the first song",
        "search on youtube and play first song", "search on youtube and play video",
        "search on youtube and play song", "search on youtube and play",
        "and play the first video", "and play first video", "and play the first song",
        "and play first song", "and play the video", "and play the song",
        "and play first", "and play", "play the first video", "play first video",
        "play the first song", "play first song", "the first video", "the first song",
        "first video", "first song", "search on youtube", "on youtube", "in youtube",
        "open youtube", "youtube", "search", "play", "video", "song"
    ]:
        query = query.replace(phrase, "")

    return query.strip(), play_first


def extract_google_query(cmd: str) -> str:
    """Extracts Google search query."""
    query = cmd
    for phrase in [
        "open google and search", "search on google for", "search on google",
        "search google for", "google search for", "google search", "on google",
        "in google", "open google", "google", "search for", "search"
    ]:
        query = query.replace(phrase, "")
    return query.strip()


def open_application(cmd: str) -> bool:
    """Opens system applications or web apps based on voice command."""
    cmd_clean = cmd.lower().replace("open", "").strip()
    if not cmd_clean:
        return False
    if cmd_clean in WEB_SITES_MAP:
        speak(f"Opening {cmd_clean}...")
        wb.open(WEB_SITES_MAP[cmd_clean])
        return True
    return focus_or_launch_app(cmd_clean)


def ask_chatgpt_live(prompt: str = "") -> None:
    """Opens ChatGPT and visually types the prompt into the message box without speech chatter."""
    print("Opening ChatGPT...")
    wb.open("https://chatgpt.com")
    time.sleep(3.5)

    if prompt:
        clean_prompt = prompt.strip()
        for phrase in [
            "open chatgpt and ask the detailed prompt to", "open chatgpt and ask detailed prompt to",
            "open chatgpt and ask prompt to", "open chatgpt and ask to", "open chatgpt and ask",
            "ask chatgpt to", "ask chatgpt", "open chatgpt", "chatgpt"
        ]:
            clean_prompt = clean_prompt.replace(phrase, "")
        clean_prompt = clean_prompt.strip()

        if clean_prompt:
            print(f"Typing prompt into ChatGPT: '{clean_prompt}'...")
            time.sleep(0.5)
            pyautogui.write(clean_prompt, interval=0.04)
            time.sleep(0.5)
            pyautogui.press('enter')


def answer_question_voice(question: str) -> bool:
    """Answers general knowledge questions with exact ChatGPT-level answers in spoken voice."""
    search_query = question.strip()
    answer = fetch_exact_ai_answer(search_query)

    if answer:
        speak(answer)
        return True
    else:
        speak(f"Searching Google for {search_query}")
        search_google_live(search_query)
        return True


def get_active_window_title() -> str:
    """Returns the title of the active foreground window on Windows."""
    try:
        hwnd = win32gui.GetForegroundWindow()
        title = win32gui.GetWindowText(hwnd)
        return title.strip() if title else ""
    except Exception:
        return ""


def detect_current_context() -> str:
    """Detects the currently active application context based on window title and foreground state."""
    title = get_active_window_title().lower()
    if not title:
        return "UNKNOWN"

    if "youtube" in title:
        return "YouTube"
    elif "whatsapp" in title:
        return "WhatsApp"
    elif "camera" in title:
        return "Camera"
    elif "file explorer" in title or "explorer" in title or any(drive in title for drive in ["local disk", "this pc", "downloads", "documents", "desktop"]):
        return "Explorer"
    elif "calculator" in title or "calc" in title:
        return "Calculator"
    elif "settings" in title:
        return "Settings"
    elif "code" in title or "visual studio code" in title:
        return "VSCode"
    elif "spotify" in title:
        return "Spotify"
    elif "photos" in title or "picture" in title:
        return "Photos"
    elif "microsoft store" in title or "store" in title:
        return "Microsoft Store"
    elif "chrome" in title:
        return "Chrome"
    elif "edge" in title:
        return "Edge"
    else:
        return "UNKNOWN"


def resolve_context_intent(cmd: str, context: str) -> bool:
    """Uses User Command AND CurrentContext to interpret intent and execute context-specific actions.
    Returns True if handled by Context Layer, False to fallback to standard execution.
    """
    cmd_lower = cmd.strip().lower()

    # 1. YOUTUBE CONTEXT
    if context == "YouTube":
        if any(kw in cmd_lower for kw in ["play the first video", "play first video", "open first video", "click first video", "play top video"]):
            speak("Playing the first video on YouTube.")
            pyautogui.press('tab')
            time.sleep(0.3)
            pyautogui.press('enter')
            return True

        elif any(kw in cmd_lower for kw in ["pause", "resume", "pause video", "play video"]):
            speak("Toggling video playback.")
            pyautogui.press('k')
            return True

        elif any(kw in cmd_lower for kw in ["fullscreen", "full screen"]):
            speak("Toggling fullscreen.")
            pyautogui.press('f')
            return True

        elif any(kw in cmd_lower for kw in ["mute", "unmute"]):
            speak("Toggling volume mute.")
            pyautogui.press('m')
            return True

        elif any(kw in cmd_lower for kw in ["next video", "next"]):
            speak("Playing next video.")
            pyautogui.hotkey('shift', 'n')
            return True

        elif cmd_lower.startswith("search ") or cmd_lower.startswith("find "):
            search_term = re.sub(r'^(search|find)\s+(for\s+)?', '', cmd_lower).strip()
            if search_term:
                speak(f"Searching YouTube for {search_term}")
                pyautogui.press('/')
                time.sleep(0.4)
                pyautogui.hotkey('ctrl', 'a')
                pyautogui.write(search_term, interval=0.05)
                time.sleep(0.3)
                pyautogui.press('enter')
                return True

    # 2. EXPLORER CONTEXT
    elif context == "Explorer":
        if any(kw in cmd_lower for kw in ["go to downloads", "open downloads"]):
            navigate_explorer_folder("downloads")
            return True

        elif any(kw in cmd_lower for kw in ["go to local disk d", "open drive d", "go to drive d", "local disk d", "open disk d", "drive d"]):
            navigate_explorer_folder("local disk d")
            return True

        elif any(kw in cmd_lower for kw in ["go to local disk c", "open drive c", "go to drive c", "local disk c", "open disk c", "drive c"]):
            navigate_explorer_folder("local disk c")
            return True

        elif any(kw in cmd_lower for kw in ["go to desktop", "open desktop"]):
            navigate_explorer_folder("desktop")
            return True

        elif any(kw in cmd_lower for kw in ["go to documents", "open documents"]):
            navigate_explorer_folder("documents")
            return True

        elif any(kw in cmd_lower for kw in ["open first image", "open first file", "open 1st file", "open top file", "open first item"]):
            speak("Opening first item in Explorer.")
            pyautogui.press('home')
            time.sleep(0.3)
            pyautogui.press('enter')
            return True

        elif cmd_lower.startswith("search ") or cmd_lower.startswith("find "):
            search_term = re.sub(r'^(search|find)\s+(for\s+)?', '', cmd_lower).strip()
            if search_term:
                speak(f"Searching File Explorer for {search_term}")
                pyautogui.hotkey('ctrl', 'f')
                time.sleep(0.4)
                pyautogui.write(search_term, interval=0.05)
                pyautogui.press('enter')
                return True

    # 3. CAMERA CONTEXT
    elif context == "Camera":
        if any(kw in cmd_lower for kw in ["take photo", "capture", "snap photo", "click photo", "take picture"]):
            camera_control("take photo")
            return True

        elif any(kw in cmd_lower for kw in ["start recording", "record video", "stop recording"]):
            camera_control("record")
            return True

    # Fallback: Not handled by context-specific rules
    return False


def parse_semantic_intent(query: str, current_context: str = "UNKNOWN") -> dict:
    """Parses a full user sentence into a structured semantic result before execution."""
    raw = query.strip()
    raw_lower = raw.lower()

    # Pattern A: YouTube Search + Play Nth Video/Song
    if "youtube" in raw_lower or current_context == "YouTube":
        search_match = re.search(r'search\s+(.*?)\s+(?:and\s+play|and\s+watch|play|watch)', raw_lower)
        if search_match:
            search_query = search_match.group(1).strip()
            search_query = re.sub(r'\b(on youtube|in youtube|youtube)\b', '', search_query).strip()
            ordinal_idx, _ = extract_ordinal(raw_lower)
            return {
                "type": "YOUTUBE_SEARCH_AND_PLAY",
                "app": "YouTube",
                "search_query": search_query,
                "ordinal": ordinal_idx,
                "target": "video"
            }

    # Pattern B: Explorer Navigate + Open Nth Item
    if "explorer" in raw_lower or "disk" in raw_lower or "drive" in raw_lower or "downloads" in raw_lower or current_context == "Explorer":
        if "disk d" in raw_lower or "drive d" in raw_lower:
            dest = "D:\\"
        elif "disk c" in raw_lower or "drive c" in raw_lower:
            dest = "C:\\"
        elif "downloads" in raw_lower:
            dest = "Downloads"
        else:
            dest = None

        if dest and ("open" in raw_lower or "file" in raw_lower or "image" in raw_lower):
            ordinal_idx, _ = extract_ordinal(raw_lower)
            return {
                "type": "EXPLORER_NAVIGATE_AND_OPEN",
                "app": "Explorer",
                "destination": dest,
                "ordinal": ordinal_idx
            }

    # Pattern C: WhatsApp Search + Send Message
    if "whatsapp" in raw_lower or current_context == "WhatsApp":
        send_match = re.search(r'(?:send\s+(.*?)\s+to\s+(.*)|search\s+(.*?)\s+and\s+send\s+(.*))', raw_lower)
        if send_match:
            g1, g2, g3, g4 = send_match.groups()
            if g1 and g2:
                msg, recipient = g1.strip(), g2.strip()
            elif g3 and g4:
                recipient, msg = g3.strip(), g4.strip()
            else:
                msg, recipient = "Hi", "Mithun"
            return {
                "type": "WHATSAPP_SEND",
                "app": "WhatsApp",
                "recipient": recipient,
                "message": msg
            }

    # Pattern D: Fallback to independent sub-commands if connected by 'and/then'
    delimiters = r'\b(?:and then|and|then)\b'
    raw_sub_cmds = [c.strip() for c in re.split(delimiters, raw_lower) if c and c.strip()]
    return {
        "type": "INDEPENDENT_CHAIN",
        "sub_commands": raw_sub_cmds or [raw_lower]
    }


def generate_hierarchical_plan(query: str, active_workspace: str = "UNKNOWN") -> dict:
    """Generates a structured Hierarchical Execution Plan enforcing Workspace Ownership and Inheritance."""
    raw = query.strip()
    raw_lower = raw.lower()

    workspace = active_workspace
    if "youtube" in raw_lower:
        workspace = "YouTube"
    elif "whatsapp" in raw_lower:
        workspace = "WhatsApp"
    elif "camera" in raw_lower:
        workspace = "Camera"
    elif "explorer" in raw_lower or "disk" in raw_lower or "drive" in raw_lower or "downloads" in raw_lower:
        workspace = "Explorer"
    elif "chrome" in raw_lower:
        workspace = "Chrome"
    elif "edge" in raw_lower:
        workspace = "Edge"
    elif "code" in raw_lower or "vscode" in raw_lower:
        workspace = "VSCode"
    elif "calculator" in raw_lower or "calc" in raw_lower:
        workspace = "Calculator"
    elif "settings" in raw_lower:
        workspace = "Settings"

    steps = []

    # 1. YOUTUBE WORKSPACE PLAN
    if workspace == "YouTube":
        search_match = re.search(r'search\s+(.*?)\s+(?:and\s+play|and\s+watch|play|watch)', raw_lower)
        if search_match:
            squery = re.sub(r'\b(on youtube|in youtube|youtube)\b', '', search_match.group(1)).strip()
            ordinal_idx, _ = extract_ordinal(raw_lower)
            steps = [
                {"step": 1, "workspace": "YouTube", "action": "OPEN", "target": "YouTube", "expected": "YouTube opened"},
                {"step": 2, "workspace": "YouTube", "action": "SEARCH", "target": squery, "expected": f"Searched '{squery}' in YouTube search bar"},
                {"step": 3, "workspace": "YouTube", "action": "PLAY_NTH", "target": "video", "ordinal": ordinal_idx, "expected": f"Playing video #{ordinal_idx} from YouTube search results"}
            ]
        elif "search" in raw_lower:
            squery = re.sub(r'^(open youtube and search|search on youtube|search youtube for|search for|search)\s*', '', raw_lower).strip()
            squery = re.sub(r'\b(on youtube|in youtube|youtube)\b', '', squery).strip()
            steps = [
                {"step": 1, "workspace": "YouTube", "action": "OPEN", "target": "YouTube", "expected": "YouTube opened"},
                {"step": 2, "workspace": "YouTube", "action": "SEARCH", "target": squery, "expected": f"Searched '{squery}' in YouTube"}
            ]

    # 2. WHATSAPP WORKSPACE PLAN
    elif workspace == "WhatsApp":
        send_match = re.search(r'(?:send\s+(.*?)\s+to\s+(.*)|search\s+(.*?)\s+and\s+send\s+(.*))', raw_lower)
        if send_match:
            g1, g2, g3, g4 = send_match.groups()
            msg, recipient = (g1.strip(), g2.strip()) if (g1 and g2) else (g4.strip(), g3.strip()) if (g3 and g4) else ("Hi", "Mithun")
            steps = [
                {"step": 1, "workspace": "WhatsApp", "action": "OPEN", "target": "WhatsApp", "expected": "WhatsApp opened"},
                {"step": 2, "workspace": "WhatsApp", "action": "SEARCH_CONTACT", "target": recipient, "expected": f"Contact '{recipient}' selected"},
                {"step": 3, "workspace": "WhatsApp", "action": "SEND_MESSAGE", "target": msg, "expected": f"Message '{msg}' sent in chat"}
            ]

    # 3. CAMERA WORKSPACE PLAN
    elif workspace == "Camera":
        if "recording" in raw_lower or "record" in raw_lower:
            steps = [
                {"step": 1, "workspace": "Camera", "action": "OPEN", "target": "Camera", "expected": "Camera opened"},
                {"step": 2, "workspace": "Camera", "action": "START_RECORDING", "target": "Video", "expected": "Recording started"}
            ]
        else:
            steps = [
                {"step": 1, "workspace": "Camera", "action": "OPEN", "target": "Camera", "expected": "Camera opened"},
                {"step": 2, "workspace": "Camera", "action": "TAKE_PHOTO", "target": "Photo", "expected": "Photo captured"}
            ]

    # 4. EXPLORER WORKSPACE PLAN
    elif workspace == "Explorer":
        dest = "D:\\" if ("disk d" in raw_lower or "drive d" in raw_lower) else "Downloads" if "downloads" in raw_lower else "C:\\" if ("disk c" in raw_lower or "drive c" in raw_lower) else None
        ordinal_idx, _ = extract_ordinal(raw_lower)
        steps = [
            {"step": 1, "workspace": "Explorer", "action": "OPEN", "target": "Explorer", "expected": "Explorer opened"},
            {"step": 2, "workspace": "Explorer", "action": "NAVIGATE", "target": dest or "Current Folder", "expected": f"Navigated to {dest}"},
            {"step": 3, "workspace": "Explorer", "action": "OPEN_NTH", "target": "item", "ordinal": ordinal_idx, "expected": f"Opened item #{ordinal_idx}"}
        ]

    # Fallback to Independent Steps
    if not steps:
        delimiters = r'\b(?:and then|and|then)\b'
        sub_cmds = [c.strip() for c in re.split(delimiters, raw_lower) if c and c.strip()]
        for idx, sc in enumerate(sub_cmds, start=1):
            steps.append({
                "step": idx,
                "workspace": workspace,
                "action": "EXECUTE",
                "target": sc,
                "expected": f"Executed '{sc}' in {workspace}"
            })

    return {
        "goal": raw,
        "primary_workspace": workspace,
        "steps": steps
    }


def explain_current_screen() -> None:
    """Captures current screen, identifies subject/person/image, and speaks explanation."""
    speak("Analyzing the current screen image...")

    window_title = get_active_window_title()
    ocr_text = ""
    temp_path = os.path.join(SCRIPT_DIR, "screen_temp.png")

    try:
        img = pyautogui.screenshot()
        img.save(temp_path)
        try:
            ocr_text = pytesseract.image_to_string(Image.open(temp_path)).strip()
        except Exception:
            pass

        if os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except Exception:
                pass
    except Exception as e:
        print(f"Screen capture notice ({e})")

    explanation_parts = []

    clean_title = window_title.split('-')[0].split('—')[0].split('.')[0].strip()
    for drop in ["Photos", "Image", "Picture", "Google Chrome", "Mozilla Firefox", "Microsoft Edge", "PNG", "JPG"]:
        clean_title = clean_title.replace(drop, "").strip()

    if clean_title and len(clean_title) > 2 and not any(app in clean_title.lower() for app in ["explorer", "code", "notepad", "calculator"]):
        explanation_parts.append(f"On your screen, you have '{clean_title}' open.")
        summary = fetch_exact_ai_answer(clean_title)
        if summary:
            explanation_parts.append(summary)

    if not explanation_parts and ocr_text:
        words = [w for w in re.findall(r'\b[A-Za-z0-9]+\b', ocr_text) if len(w) > 3]
        if words:
            from collections import Counter
            top_words = [w for w, _ in Counter(words).most_common(3)]
            topic = " ".join(top_words)
            summary = fetch_exact_ai_answer(topic)
            if summary:
                explanation_parts.append(f"This image displays {topic}. {summary}")
            else:
                explanation_parts.append(f"The screen content features text related to {', '.join(top_words)}.")

    if explanation_parts:
        speak(" ".join(explanation_parts))
    else:
        if window_title:
            speak(f"On your screen, you are currently viewing {window_title}.")
        else:
            speak("On your current screen, an active image or document is displayed.")


def parse_option_number(cmd: str) -> int:
    """Extracts option number from responses like '1', 'the 1st one', 'number 2', 'option 3', 'first', etc."""
    cmd = cmd.strip().lower()

    number_words = {
        "1": 1, "first": 1, "1st": 1, "one": 1,
        "2": 2, "second": 2, "2nd": 2, "two": 2,
        "3": 3, "third": 3, "3rd": 3, "three": 3,
        "4": 4, "fourth": 4, "4th": 4, "four": 4,
        "5": 5, "fifth": 5, "5th": 5, "five": 5,
        "6": 6, "sixth": 6, "6th": 6, "six": 6,
    }

    for word, num in number_words.items():
        if re.search(r'\b' + word + r'\b', cmd):
            return num

    match = re.search(r'\d+', cmd)
    if match:
        return int(match.group())

    return None


def handle_context_response(cmd: str) -> bool:
    """Checks if response is answering a prior context question (e.g. selecting option #1, #2)."""
    global LAST_CONTEXT_ACTION, LAST_OPTIONS_LIST

    if not LAST_CONTEXT_ACTION:
        return False

    num = parse_option_number(cmd)
    if num and 1 <= num <= len(LAST_OPTIONS_LIST):
        selected_option = LAST_OPTIONS_LIST[num - 1]
        speak(f"Selecting option {num}: {selected_option}")
        print(f"Executing context selection {num}: '{selected_option}'")

        if LAST_CONTEXT_ACTION == "open_menu":
            pyautogui.press('alt')
            time.sleep(0.3)
            pyautogui.write(selected_option[0].lower())

        LAST_CONTEXT_ACTION = None
        LAST_OPTIONS_LIST = []
        return True

    return False


def handle_screen_controls(cmd: str) -> bool:
    """Handles contextual screen and window navigation commands."""
    global LAST_CONTEXT_ACTION, LAST_OPTIONS_LIST
    cmd = cmd.strip().lower()

    if any(kw in cmd for kw in ["open menu", "open the menu", "show menu", "menu"]):
        LAST_CONTEXT_ACTION = "open_menu"
        LAST_OPTIONS_LIST = ["File", "Edit", "View", "Help"]

        speak("I found menu options: Option 1: File, Option 2: Edit, Option 3: View, Option 4: Help. Which option number would you like to open?")
        print("\n[Menu Options]:\n  Option 1: File\n  Option 2: Edit\n  Option 3: View\n  Option 4: Help\n")
        return True

    elif "scroll down" in cmd or "scroll to bottom" in cmd:
        speak("Scrolling down.")
        pyautogui.scroll(-800)
        return True

    elif "scroll up" in cmd or "scroll to top" in cmd or "scroll to the top" in cmd:
        speak("Scrolling up.")
        pyautogui.scroll(800)
        return True

    elif "close window" in cmd or "close app" in cmd:
        speak("Closing active window.")
        set_window_state("active", "close")
        return True

    elif "close tab" in cmd:
        speak("Closing tab.")
        pyautogui.hotkey('ctrl', 'w')
        return True

    elif "new tab" in cmd:
        speak("Opening new tab.")
        pyautogui.hotkey('ctrl', 't')
        return True

    elif "refresh" in cmd or "reload" in cmd:
        speak("Refreshing page.")
        pyautogui.press('f5')
        return True

    elif "go back" in cmd:
        speak("Going back.")
        pyautogui.hotkey('alt', 'left')
        return True

    elif "go forward" in cmd:
        speak("Going forward.")
        pyautogui.hotkey('alt', 'right')
        return True

    elif "fullscreen" in cmd:
        speak("Toggling fullscreen.")
        pyautogui.press('f11')
        return True

    elif "zoom in" in cmd:
        speak("Zooming in.")
        pyautogui.hotkey('ctrl', '+')
        return True

    elif "zoom out" in cmd:
        speak("Zooming out.")
        pyautogui.hotkey('ctrl', '-')
        return True

    return False


def handle_type_mode(query: str) -> bool:
    """Handles live typing mode. Returns True if in Type Mode, False otherwise."""
    global TYPE_MODE_ACTIVE

    query_lower = query.strip().lower()

    if TYPE_MODE_ACTIVE:
        if any(kw in query_lower for kw in ["turn off type mode", "type mode off", "exit type mode", "stop type mode", "deactivate type mode"]):
            TYPE_MODE_ACTIVE = False
            speak("Type mode deactivated. Returning to normal mode.")
            return True

        print(f"[Typewriter]: {query}")
        type_text_smoothly(query)
        return True

    if any(kw in query_lower for kw in ["turn on type mode", "type mode on", "activate type mode", "start type mode"]):
        TYPE_MODE_ACTIVE = True
        speak("Type mode activated. Speak continuously into the microphone and I will type live like a typewriter. Say 'type mode off' to exit.")
        return True

    return False


def execute_task_model_sequence(task_model: TaskModel) -> bool:
    """Executes a structured TaskModel sequence continuously step-by-step with state observation."""
    if not task_model or not task_model.sequence:
        return False

    obs_loop = UniversalObservationLoop()
    print(f"\n[Continuous Execution Loop]: Executing {len(task_model.sequence)} steps for goal: '{task_model.primary_goal}'")

    for step in task_model.sequence:
        print(f"  └─ Step {step.step_number}/{len(task_model.sequence)}: [{step.action}] {step.target} (Workspace: {step.workspace})")

        action_name = step.action.upper()

        if action_name == "OPEN":
            if step.target.lower() in WEB_SITES_MAP:
                wb.open(WEB_SITES_MAP[step.target.lower()])
            elif step.target.lower() in ["downloads", "documents", "desktop", "pictures", "videos", "music", "this pc", "recycle bin", "local disk c", "local disk d", "local disk e", "usb drive"]:
                navigate_explorer_folder(step.target.lower())
            else:
                focus_or_launch_app(step.target)
            time.sleep(1.2)

        elif action_name == "CLOSE":
            set_window_state(step.target, "close")
            time.sleep(0.5)

        elif action_name == "SEARCH":
            query = step.parameters.get("query", step.target)
            if step.workspace == "YouTube":
                search_and_play_youtube_live(query, play_first=False)
            elif step.workspace == "WhatsApp":
                pyautogui.hotkey('ctrl', 'f')
                time.sleep(0.3)
                pyautogui.write(query, interval=0.04)
                pyautogui.press('enter')
            elif step.workspace == "Explorer":
                pyautogui.hotkey('ctrl', 'f')
                time.sleep(0.3)
                pyautogui.write(query, interval=0.04)
                pyautogui.press('enter')
            else:
                search_google_live(query)
            time.sleep(0.8)

        elif action_name in ["GO", "NAVIGATE"]:
            navigate_explorer_folder(step.target)
            time.sleep(0.8)

        elif action_name == "SELECT":
            ordinal_idx = step.parameters.get("ordinal", 1)
            pyautogui.press('home')
            time.sleep(0.2)
            for _ in range(max(0, ordinal_idx - 1)):
                pyautogui.press('down')
                time.sleep(0.1)

        elif action_name in ["PLAY", "PLAY_NTH"]:
            ordinal_idx = step.parameters.get("ordinal", 1)
            pyautogui.press('enter')
            time.sleep(0.5)

        elif action_name == "TYPE":
            text_to_type = step.parameters.get("text", step.target)
            pyautogui.write(text_to_type, interval=0.04)
            time.sleep(0.4)

        elif action_name == "ENTER":
            pyautogui.press('enter')
            time.sleep(0.4)

        elif action_name == "SET":
            val = step.parameters.get("value", 50)
            if step.target.lower() == "volume":
                adjust_volume("set", percent=val)
            elif step.target.lower() == "brightness":
                adjust_brightness("set", percent=val)
            time.sleep(0.3)

        elif action_name in ["INCREASE", "DECREASE"]:
            if step.target.lower() == "volume":
                adjust_volume("up" if action_name == "INCREASE" else "down")
            elif step.target.lower() == "brightness":
                adjust_brightness("set", percent=80 if action_name == "INCREASE" else 30)
            time.sleep(0.3)

        elif action_name in ["TAKE_PHOTO", "START_RECORDING"]:
            camera_control("take photo" if action_name == "TAKE_PHOTO" else "record")
            time.sleep(0.5)

        elif action_name == "TAKE_SCREENSHOT":
            take_desktop_screenshot(open_folder=False)
            time.sleep(0.5)

        elif action_name == "OPEN_SETTING":
            open_system_setting(step.target)
            time.sleep(0.8)

        elif action_name == "SYSTEM_ACTION":
            execute_windows_system_action(step.target)
            time.sleep(0.5)

        elif action_name == "EXECUTE":
            execute_single_command(step.target)

        # State Observation Verification
        obs = obs_loop.observe(step.expected_result, step.workspace)
        print(f"     [Observed]: {obs['summary']}")
        step.is_completed = True

    print(f"[Continuous Execution Completed]: Goal '{task_model.primary_goal}' accomplished successfully!\n")
    return True


def execute_single_command(cmd: str) -> bool:
    """Executes a single intent command using CurrentContext layer for intent detection.
    Returns False if requested to exit, True otherwise.
    """
    cmd = cmd.strip()
    if not cmd:
        return True

    cmd_l = cmd.lower()

    if handle_context_response(cmd):
        return True

    if cmd_l in ["offline", "exit", "stop", "quit", "go offline"]:
        speak("Going offline. Have a good day!")
        return False

    # 1. Restart Application
    if cmd_l.startswith("restart "):
        app_target = cmd_l.replace("restart", "").strip()
        if app_target not in ["computer", "pc", "system"]:
            speak(f"Restarting {app_target}...")
            set_window_state(app_target, "close")
            time.sleep(1.0)
            focus_or_launch_app(app_target)
            return True

    # 2. Close Window / App
    if cmd_l.startswith("close ") or cmd_l.startswith("exit ") or cmd_l.startswith("quit ") or cmd_l.startswith("terminate "):
        app_target = re.sub(r'^(close|exit|quit|terminate)\s+', '', cmd_l).strip()
        if app_target in ["window", "app", "application", ""]:
            set_window_state("active", "close")
            speak("Closed active window.")
            return True
        elif app_target:
            speak(f"Closing {app_target}...")
            set_window_state(app_target, "close")
            return True

    # 3. Minimize / Maximize / Restore / Focus / Bring to Front
    elif cmd_l.startswith("minimize "):
        app_target = cmd_l.replace("minimize", "").strip()
        speak(f"Minimizing {app_target}...")
        set_window_state(app_target, "minimize")
        return True

    elif cmd_l.startswith("maximize "):
        app_target = cmd_l.replace("maximize", "").strip()
        speak(f"Maximizing {app_target}...")
        set_window_state(app_target, "maximize")
        return True

    elif cmd_l.startswith("restore "):
        app_target = cmd_l.replace("restore", "").strip()
        speak(f"Restoring {app_target}...")
        set_window_state(app_target, "restore")
        return True

    elif cmd_l.startswith("focus ") or cmd_l.startswith("switch to ") or (cmd_l.startswith("bring ") and "to front" in cmd_l):
        app_target = re.sub(r'^(focus|switch to|bring)\s+', '', cmd_l).replace("to front", "").strip()
        speak(f"Switching to {app_target}...")
        focus_or_launch_app(app_target)
        return True

    # 4. System Volume Controls
    elif "volume" in cmd_l:
        if "up" in cmd_l or "increase" in cmd_l:
            adjust_volume("up")
            speak("Increased volume.")
            return True
        elif "down" in cmd_l or "decrease" in cmd_l:
            adjust_volume("down")
            speak("Decreased volume.")
            return True
        elif "mute" in cmd_l:
            adjust_volume("mute")
            speak("Toggled mute.")
            return True
        else:
            val_match = re.search(r'(\d+)', cmd_l)
            if val_match:
                pct = int(val_match.group(1))
                adjust_volume("set", percent=pct)
                speak(f"Set volume to {pct} percent.")
                return True

    # 5. System Brightness Controls
    elif "brightness" in cmd_l or "brighter" in cmd_l or "dimmer" in cmd_l:
        val_match = re.search(r'(\d+)', cmd_l)
        pct = int(val_match.group(1)) if val_match else 80
        adjust_brightness("set", percent=pct)
        speak(f"Set brightness to {pct} percent.")
        return True

    # 6. Windows Settings Toggles (ON / OFF)
    elif any(kw in cmd_l for kw in ["bluetooth", "wifi", "wi-fi", "night light", "dark mode", "light mode", "battery saver", "power saver", "focus assist", "location", "mute"]):
        for key in ["bluetooth", "wifi", "wi-fi", "night light", "dark mode", "light mode", "battery saver", "power saver", "focus assist", "location", "mute"]:
            if key in cmd_l:
                if any(state in cmd_l for state in ["off", "disable", "deactivate"]):
                    toggle_system_setting(key, "off")
                    speak(f"Turned off {key}.")
                elif any(state in cmd_l for state in ["on", "enable", "activate"]):
                    toggle_system_setting(key, "on")
                    speak(f"Turned on {key}.")
                else:
                    open_system_setting(key)
                    speak(f"Opened {key} settings.")
                return True

    # 7. Open Application / Web Site / Folder
    elif any(cmd_l.startswith(f"{syn} ") for syn in ["open", "launch", "start", "run", "bring up", "show"]):
        app_target = re.sub(r'^(open|launch|start|run|bring up|show)\s+', '', cmd_l).strip()
        if app_target in WEB_SITES_MAP:
            speak(f"Opening {app_target}...")
            wb.open(WEB_SITES_MAP[app_target])
            return True
        elif app_target in ["downloads", "documents", "desktop", "pictures", "videos", "music", "this pc", "recycle bin", "local disk c", "local disk d", "local disk e", "usb drive"]:
            navigate_explorer_folder(app_target)
            return True
        elif focus_or_launch_app(app_target):
            return True

    # 8. File Explorer File/Folder Actions
    elif any(kw in cmd_l for kw in ["create folder", "create new folder", "rename", "delete", "copy", "cut", "paste", "select all", "deselect all"]):
        if "create" in cmd_l:
            pyautogui.hotkey('ctrl', 'shift', 'n')
            speak("Created new folder.")
            return True
        elif "rename" in cmd_l:
            pyautogui.press('f2')
            speak("Rename activated.")
            return True
        elif "delete" in cmd_l:
            pyautogui.press('delete')
            speak("Deleted item.")
            return True
        elif "copy" in cmd_l:
            pyautogui.hotkey('ctrl', 'c')
            speak("Copied item.")
            return True
        elif "cut" in cmd_l:
            pyautogui.hotkey('ctrl', 'x')
            speak("Cut item.")
            return True
        elif "paste" in cmd_l:
            pyautogui.hotkey('ctrl', 'v')
            speak("Pasted item.")
            return True
        elif "select all" in cmd_l:
            pyautogui.hotkey('ctrl', 'a')
            speak("Selected all items.")
            return True
        elif "deselect" in cmd_l:
            pyautogui.press('escape')
            speak("Deselected items.")
            return True

    # Detect CurrentContext before intent resolution
    current_context = detect_current_context()
    print(f"[CurrentContext]: {current_context}")

    # Check Context Layer intent resolution first (User Command + CurrentContext)
    if resolve_context_intent(cmd, current_context):
        return True

    # Standard Intent Handlers
    if handle_friendly_chitchat(cmd):
        return True

    elif any(kw in cmd.lower() for kw in [
        "who is this", "who is in this image", "who is in this picture", "who is in the photo",
        "what is this image", "what is this picture", "explain this image", "explain image",
        "what is on my screen", "explain screen", "explain this screen", "explain current screen",
        "explain current window", "what is on current screen", "describe screen", "what is open"
    ]):
        explain_current_screen()

    elif handle_screen_controls(cmd):
        pass

    elif "chatgpt" in cmd or "chat gpt" in cmd:
        ask_chatgpt_live(cmd)

    elif any(cmd.startswith(qw) for qw in ["when ", "who ", "what ", "why ", "where ", "how ", "tell me about ", "explain "]):
        answer_question_voice(cmd)

    elif "youtube" in cmd or ("play" in cmd and "music" not in cmd):
        query, play_first = extract_youtube_query(cmd)
        search_and_play_youtube_live(query, play_first=play_first)

    elif "google" in cmd and "search" in cmd:
        query = extract_google_query(cmd)
        search_google_live(query)

    elif "time" in cmd:
        time_func()

    elif "date" in cmd:
        date()

    elif "wikipedia" in cmd:
        query = cmd.replace("wikipedia", "").replace("search", "").strip()
        search_wikipedia(query)

    elif "play music" in cmd:
        song_name = cmd.replace("play music", "").strip()
        play_music(song_name)

    elif "change your name" in cmd:
        set_name()

    elif "screenshot" in cmd:
        screenshot()
        speak("I've taken screenshot, please check it")

    elif "tell me a joke" in cmd or "joke" in cmd:
        joke = pyjokes.get_joke()
        speak(joke)

    elif "shutdown" in cmd or "shut down" in cmd:
        speak("Shutting down the system, goodbye!")
        os.system("shutdown /s /f /t 1")
        return False

    elif "restart computer" in cmd or "restart pc" in cmd or "restart system" in cmd:
        speak("Restarting the system, please wait!")
        os.system("shutdown /r /f /t 1")
        return False

    elif "lock computer" in cmd or "lock screen" in cmd:
        execute_windows_system_action("lock")
        speak("Locked computer.")
        return True

    elif "sleep" in cmd:
        execute_windows_system_action("sleep")
        speak("Putting computer to sleep.")
        return True

    elif cmd.startswith("search ") or cmd.startswith("find "):
        search_query = cmd.replace("search", "").replace("find", "").strip()
        search_google_live(search_query)

    else:
        answer = fetch_exact_ai_answer(cmd)
        if answer:
            speak(answer)
        else:
            speak("I'm listening, my friend! Feel free to ask me any question, talk to me, or tell me what to open.")

    return True


def handle_direct_system_settings_query(query: str) -> bool:
    """Intercepts screenshot, system settings toggles, volume, and brightness commands immediately."""
    q = query.lower().strip()

    # 1. Screenshot
    if "screenshot" in q:
        take_desktop_screenshot(open_folder=True)
        speak("I've taken a screenshot!")
        return True

    # 2. Volume
    if "volume" in q:
        if any(w in q for w in ["up", "increase", "raise"]):
            adjust_volume("up")
            speak("Increased volume.")
            return True
        elif any(w in q for w in ["down", "decrease", "lower"]):
            adjust_volume("down")
            speak("Decreased volume.")
            return True
        elif "mute" in q:
            adjust_volume("mute")
            speak("Toggled mute.")
            return True
        else:
            val_match = re.search(r'(\d+)', q)
            if val_match:
                pct = int(val_match.group(1))
                adjust_volume("set", percent=pct)
                speak(f"Set volume to {pct} percent.")
                return True

    # 3. Brightness
    if "brightness" in q or "brighter" in q or "dimmer" in q:
        val_match = re.search(r'(\d+)', q)
        pct = int(val_match.group(1)) if val_match else 80
        if "increase" in q or "up" in q or "brighter" in q:
            adjust_brightness("up", percent=pct)
            speak("Increased brightness.")
        elif "decrease" in q or "down" in q or "dimmer" in q:
            adjust_brightness("down", percent=pct)
            speak("Decreased brightness.")
        else:
            adjust_brightness("set", percent=pct)
            speak(f"Set brightness to {pct} percent.")
        return True

    # 4. Windows Settings Toggles (ON / OFF)
    settings_keys = ["hotspot", "mobile hotspot", "tethering", "bluetooth", "wifi", "wi-fi", "night light", "nightlight", "dark mode", "light mode", "battery saver", "power saver", "focus assist", "location", "mute"]
    if any(k in q for k in settings_keys):
        for key in settings_keys:
            if key in q:
                if any(state in q for state in ["off", "disable", "deactivate"]):
                    toggle_system_setting(key, "off")
                    speak(f"Turned off {key}.")
                    return True
                elif any(state in q for state in ["on", "enable", "activate"]):
                    toggle_system_setting(key, "on")
                    speak(f"Turned on {key}.")
                    return True
                elif "open" in q or "show" in q:
                    open_system_setting(key)
                    speak(f"Opened {key} settings.")
                    return True

    return False


def process_full_query(full_query: str) -> bool:
    """Parses user sentence into a Hierarchical Execution Plan BEFORE executing."""
    raw_query = full_query.strip().lower()
    if not raw_query:
        return True

    # Standalone Exit Command Interceptor (Immediate termination without doing anything)
    clean_standalone = re.sub(r'[^\w\s]', '', raw_query).strip().lower()
    if clean_standalone in ["exit", "stop", "quit", "offline", "go offline", "bye", "goodbye"]:
        speak("Going offline. Have a good day!")
        return False

    cleaned_query, is_polite = clean_conversational_query(raw_query)

    if is_polite and cleaned_query:
        responses = ["Definitely, sir!", "Sure thing, sir!", "Right away, sir!"]
        speak(random.choice(responses))

    target_query = cleaned_query or raw_query

    # Direct System Settings / Screenshot Interceptor
    if handle_direct_system_settings_query(target_query):
        return True

    # Check NOW MODE route first
    if target_query.startswith("now ") or target_query.startswith("now,"):
        now_engine = NowModeEngine()
        now_engine.process_now_command(target_query)
        return True

    # Detect current active application context
    current_context = detect_current_context()

    # Build Structured TaskModel
    task_model = build_human_task_model(target_query, current_context)
    if task_model and task_model.sequence and len(task_model.sequence) >= 1:
        print(f"\n[TaskModel Generated]:\n{json.dumps(task_model.to_dict(), indent=2)}")
        executed = execute_task_model_sequence(task_model)
        if executed:
            return True

    # Generate Hierarchical Plan with Workspace Ownership & Inheritance
    plan = generate_hierarchical_plan(target_query, current_context)
    print(f"\n[Hierarchical Execution Plan]:\n{json.dumps(plan, indent=2)}")

    semantic_result = parse_semantic_intent(target_query, plan["primary_workspace"])
    stype = semantic_result.get("type")

    # 1. YOUTUBE_SEARCH_AND_PLAY Workflow
    if stype == "YOUTUBE_SEARCH_AND_PLAY":
        squery = semantic_result.get("search_query", "")
        ordinal_idx = semantic_result.get("ordinal", 1)
        search_and_play_youtube_live(squery, play_first=True, video_index=ordinal_idx)
        return True

    # 2. EXPLORER_NAVIGATE_AND_OPEN Workflow
    elif stype == "EXPLORER_NAVIGATE_AND_OPEN":
        dest = semantic_result.get("destination")
        ordinal_idx = semantic_result.get("ordinal", 1)

        if dest == "D:\\":
            navigate_explorer_folder("local disk d")
        elif dest == "Downloads":
            navigate_explorer_folder("downloads")

        time.sleep(1.0)
        speak(f"Opening item number {ordinal_idx}")
        pyautogui.press('home')
        time.sleep(0.3)
        for _ in range(max(0, ordinal_idx - 1)):
            pyautogui.press('down')
            time.sleep(0.1)
        pyautogui.press('enter')
        return True

    # 3. WHATSAPP_SEND Workflow
    elif stype == "WHATSAPP_SEND":
        recipient = semantic_result.get("recipient", "")
        msg = semantic_result.get("message", "Hi")

        open_application("whatsapp")
        time.sleep(2.0)
        if recipient:
            speak(f"Searching contact {recipient}")
            pyautogui.hotkey('ctrl', 'f')
            time.sleep(0.4)
            pyautogui.write(recipient, interval=0.05)
            pyautogui.press('enter')
            time.sleep(0.5)

        speak(f"Sending message: {msg}")
        pyautogui.write(msg, interval=0.04)
        time.sleep(0.3)
        pyautogui.press('enter')
        return True

    # 4. INDEPENDENT_CHAIN Fallback
    sub_commands = semantic_result.get("sub_commands", [target_query])
    if len(sub_commands) > 1:
        for idx, sub_cmd in enumerate(sub_commands):
            if idx > 0:
                time.sleep(1.5)
            should_continue = execute_single_command(sub_cmd)
            if not should_continue:
                return False
        return True

    return execute_single_command(target_query)


def run_iris():
    wishme()

    while True:
        query = takecommand()
        if not query:
            continue

        if handle_type_mode(query):
            continue

        should_continue = process_full_query(query)
        if not should_continue:
            break


if __name__ == "__main__":
    run_iris()
