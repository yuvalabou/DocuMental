
# DocuMental: TODO & Roadmap

This document outlines potential improvements and future features for the DocuMental project.
### Fixes

- [ ] **Watchdog:** Watch instead of polling the print queue.

### Core Functionality Enhancements

- [x] **Text-to-Speech (TTS) Notifications:** Give the printer a literal voice. Instead of just a desktop notification, the LLM's response could be read aloud.
    - **Implementation:** Modify `communication.py` to include a TTS library like `pyttsx3` (for local, cross-platform speech) or `gTTS` (Google Text-to-Speech).

- [ ] **Advanced Job Interaction:** Allow the agent to take action on jobs based on the LLM's decision.
    - **Implementation:** Use the `win32print.SetJob` function to pause, resume, or cancel jobs. For example, the LLM could decide to pause a very large print job and ask the user for confirmation.

### User Experience (UX) & Configuration

- [ ] **External Configuration File:** Move hardcoded settings to a user-editable file.
    - **Implementation:** Create a `config.ini` or `config.json` file to store the `LM_STUDIO_ENDPOINT` and potentially the `SYSTEM_PROMPT`, so users don't need to edit Python files.

- [ ] **System Tray Icon:** Allow the script to run as a background application with a system tray icon for easier management.
    - **Implementation:** Use a library like `pystray` to create an icon with options like "Select Printer," "Pause/Resume," and "Exit."

### Packaging & Distribution

- [ ] **Create a `pyproject.toml`:** Modernize the project structure to make it easily packageable and installable (`pip install .`).
    - **Implementation:** Create a `pyproject.toml` file defining project metadata, dependencies, and an entry point that calls `prt_mind.main`.

- [ ] **Publish to PyPI:** Package the project and upload it to the Python Package Index.
    - **Implementation:** Use `build` and `twine` to create and upload the distribution files.

### Advanced Feature Ideas

- [ ] **Expanded Context for LLM:** Feed more job details to the LLM for more "intelligent" and varied responses.
    - **Implementation:** Pass details from the `GetJob` call like page count, data size, and submission time into the prompt for the `brain` module.

- [ ] **Multi-Channel Notifications:** Expand `communication.py` to support sending alerts to other platforms.
    - **Implementation:** Add functions to `notify_user` to send messages to Slack, Discord, or email using their respective APIs.
