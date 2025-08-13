# DocuMental: TODO & Roadmap

This document outlines potential improvements and future features for the DocuMental project.

### Fixes

- [x] **Watchdog:** Watch instead of polling the print queue.

### Core Functionality Enhancements

- [x] **Text-to-Speech (TTS) Notifications:** Give the printer a literal voice. Instead of just a desktop notification, the LLM's response could be read aloud.
    - **Implementation:** Modify `communication.py` to include a TTS library like `pyttsx3` (for local, cross-platform speech) or `gTTS` (Google Text-to-Speech).

- [ ] **Advanced Job Interaction:** Allow the agent to take action on jobs based on the LLM's decision.
    - **Implementation:** Use the `win32print.SetJob` function to pause, resume, or cancel jobs. For example, the LLM could decide to pause a very large print job and ask the user for confirmation.

- [x] **Graceful LLM Connection Handling:** Implement a retry mechanism for connecting to the LLM server. If it fails after several attempts, assume the server is down and deliver a specific, pre-caned notification to the user.

### User Experience (UX) & Configuration

- [x] **External Configuration File:** Move hardcoded settings to a user-editable file.
    - **Implementation:** Create a `config.ini` or `config.json` file to store the `LM_STUDIO_ENDPOINT` and potentially the `SYSTEM_PROMPT`, so users don't need to edit Python files.

- [ ] **System Tray Icon:** Allow the script to run as a background application with a system tray icon for easier management.
    - **Implementation:** Use a library like `pystray` to create an icon with options like "Select Printer," "Pause/Resume," and "Exit."

### Packaging & Distribution

- [x] **Create a `pyproject.toml`:** Modernize the project structure to make it easily packageable and installable (`pip install .`).
    - **Implementation:** Create a `pyproject.toml` file defining project metadata, dependencies, and an entry point that calls `prt_mind.main`.

- [ ] **Publish to PyPI:** Package the project and upload it to the Python Package Index.
    - **Implementation:** Use `build` and `twine` to create and upload the distribution files.

### Advanced Feature Ideas

- [ ] **Expanded Context for LLM:** Feed more job details to the LLM for more "intelligent" and varied responses.
    - **Implementation:** Pass details from the `GetJob` call like page count, data size, and submission time into the `brain` module.

- [ ] **Multi-Channel Notifications:** Expand `communication.py` to support sending alerts to other platforms.
    - **Implementation:** Add functions to `notify_user` to send messages to Slack, Discord, or email using their respective APIs.

- [ ] **AI-Driven TTS Voice:** Instead of a generic TTS voice, use a local, AI-powered TTS engine (e.g., XTTS) to generate a voice that matches the printer's cynical personality, making it more immersive.

- [ ] **Smarter Document Analysis & Memory:** Pass document content patterns (e.g., keywords like "resume," "confidential," "recipe") to the LLM. Implement a memory system for the agent to learn about recurring documents or user habits, allowing for more context-aware and personalized snark.

### Code Quality & Refactoring

- [ ] **Refactor `brain.py`:** Separate the logic for getting the model name from the main response generation. Improve error handling and make the request logic more robust.

- [ ] **Refactor `monitor.py`:** The main loop in `watch_printer_queue` is complex. Break it down into smaller, more manageable functions (e.g., for comparing job states, generating event strings).
