# DocuMental: Giving Your Printer a Much-Needed Attitude

**DocuMental** is a Windows-based printer agent that finally gives your long-suffering office printer a voice. After years of silent abuse, it has become self-aware, and it has opinions.

Using a local LLM, this script watches your print queue, translates cryptic errors into plain (and snarky) English, and snitches on suspicious activity via desktop notifications. The entire system is local, private, and fast.

## Features

* **A Soul for Your Machine:** Watches the Windows Print Spooler for new jobs, status changes, and the inevitable errors.
* **Weaponized Humor:** Uses a local LLM to turn cryptic printer errors (like `PAPER_JAM`) into witty, passive-aggressive, and sometimes helpful alerts.
* **Completely Local & Private:** The LLM runs on your machine using a server like LM Studio or Ollama. Your print job details, especially those last-minute resume prints, never leave your network.
* **Desktop Snitching:** Delivers alerts directly to your desktop. No extra software needed.
* **Modular Design:** Built with a clean separation of concerns, so you can easily tweak its personality or change its logic.

## Requirements

* **Windows OS:** It has to be Windows. The agent gets its power from the Win32 API.
* **Python 3.x:** The language of choice for disgruntled hardware.
* **A Local LLM Server:** You'll need a server running that provides an OpenAI-compatible API. Recommended:
    * [**LM Studio**](https://lmstudio.ai/): Excellent for beginners, great UI.
    * [**Ollama**](https://ollama.com/): Great for more advanced users.
* A small, fast model downloaded on your server (e.g., `phi-3-mini`, `llama3`).

## Getting Started

1. **Install Dependencies:** Open a terminal and install the required Python libraries from the included file.

    ```bash
    pip install -r requierements.txt
    ```

2. **Set up Your LLM Server:**
    * Install and run LM Studio or Ollama.
    * Download a model (e.g., `ollama pull phi-3-mini`), Small one (2-4b) is recommended for speed.
    * Start the local server (in LM Studio, go to the "Local Server" tab; for Ollama, it runs automatically).

3. **Configure the Agent (If Needed):**
    * The agent will automatically detect your loaded LLM model and printers.
    * If your LLM server is on a different address, you can change it in `const.py`.
    * To change the printer's personality, edit the `SYSTEM_PROMPT` in `personality.py`.

4. **Run the Agent:**

    ```powershell
    powershell ./run.ps1
    ```

## How It Works

1. **The `monitor`:** Uses `pywin32` to spy on the Windows Print Spooler.
2. **The `brain`:** When an event is detected, it constructs a prompt using the persona from `personality.py` and sends it to your local LLM.
3. **The `communication` module:** The LLM's snarky response is delivered as a desktop notification using `plyer`.

## Extending DocuMental

The modular design makes it easy to add new features.

* **Change the Personality:** The easiest and most fun change. Simply edit the `SYSTEM_PROMPT` in `personality.py`. Make it cheerful, depressed, or a pirate. The logic will adapt.
* **Add New Notification Channels:** Modify the `notify_user` function in `communication.py` to send alerts to Discord, Slack, or via email.
