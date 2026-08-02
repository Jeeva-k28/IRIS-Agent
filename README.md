# IRIS - Advanced Desktop AI Voice & Vision Assistant 🔥

<img src="https://giffiles.alphacoders.com/212/212508.gif" alt="IRIS Assistant Banner">

**IRIS** is a state-of-the-art, highly intelligent Desktop AI Voice & Vision Companion built with Python. It features Universal NOW MODE for real-time visual UI searching and direct element interaction across desktop apps and browsers, native Windows settings toggles, intelligence layers, and complete system automation.

---

## 📌 Built With

<code><img height="30" src="https://raw.githubusercontent.com/github/explore/80688e429a7d4ef2fca1e82350fe8e3517d3494d/topics/python/python.png"></code>

- **Core Assistant**: Python 3.11+
- **Voice Recognition**: PyAudio & SpeechRecognition
- **Text-To-Speech**: PyTTSx3
- **Automation & Vision**: PyAutoGUI, OpenCV, Pillow, PyTesseract, Windows UI Automation (UIA)
- **AI Models**: GPT-4o integration via `g4f` client & DDGS search

---

## 📌 Key Features

- **⚡ Universal NOW MODE**:
  - Live search widget HUD overlay for typing query and highlighting active targets.
  - Native Windows `IUIAutomation` programmatic invocation with zero mouse movement.
  - Operates on active browser tabs, File Explorer cards, YouTube, and desktop apps.
- **⚙️ System Settings Manager**:
  - Voice-activated ON / OFF toggles for Bluetooth, Wi-Fi, Night Light, Dark Mode, Mobile Hotspot, Battery Saver, Focus Assist, Location, and Mute.
  - Direct volume and screen brightness adjustment (`0-100%`).
  - Immediate desktop screenshot capture (`"now take screenshot"`).
- **🚀 Desktop & Web Workflows**:
  - YouTube live search, playback controls, and video navigation.
  - File Explorer navigation (Downloads, Documents, Local Drives).
  - Web workflow automation for Google, ChatGPT, Amazon, GitHub, WhatsApp, and more.
- **⏹️ Instant Exit Controls**:
  - Immediate clean termination with `"exit"`, `"stop"`, `"quit"`, or `"offline"`.

---

## 📌 Installation

1. **Clone The Repository**
   ```bash
   git clone https://github.com/Jeeva-k28/IRIS-Agent.git
   cd IRIS-Agent
   ```

2. **Create & Activate Virtual Environment**
   - For Windows (PowerShell):
     ```powershell
     python -m venv .venv
     .venv\Scripts\activate
     ```

3. **Install Requirements**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run IRIS**
   ```bash
   python iris.py
   # OR
   python Iris/iris.py
   ```

---

## 📌 Project Structure

```text
├── Iris/                         # Main IRIS Voice & Logic Engine
│   └── iris.py
├── desktop/                      # System & Application Controls
│   ├── desktop_core.py
│   └── system_settings_manager.py
├── now_mode/                     # Universal NOW MODE Engine & Visual Search HUD
│   ├── now_mode.py
│   ├── now_executor.py
│   ├── target_resolver.py
│   ├── uia_inspector.py
│   ├── vision_engine.py
│   └── visual_search_hud.py
├── intelligence_layer/           # Task Models, Intent Parser & Observation Loop
├── website_workflows/            # Web Automations (YouTube, ChatGPT, GitHub, etc.)
└── tests/                        # Full Automated Unit Test Suites
```

---

## 📌 Author & Maintenance

👤 **Jeeva K**
- GitHub: [@Jeeva-k28](https://github.com/Jeeva-k28)
- Project Repository: [IRIS-Agent](https://github.com/Jeeva-k28/IRIS-Agent)
