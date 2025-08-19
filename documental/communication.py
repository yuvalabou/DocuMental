"""
# The Communication Module: The Mouthpiece

This module is the agent's voice. It provides distinct channels for visual
and auditory notifications, allowing the user to see and/or hear what the
printer is thinking.
"""

import sys

import pyttsx3
from plyer import notification

# --- Global TTS Engine Initialization ---
# Initialize the Text-to-Speech (TTS) engine globally.
# This is crucial for performance, as initializing the engine can be slow.
# By creating a single instance, we can reuse it for all subsequent speech requests.
# A try-except block handles cases where a TTS engine might not be available on the system.
try:
    # pyttsx3.init() discovers and initializes the best available TTS driver on the host OS.
    engine = pyttsx3.init()
except Exception as e:
    # If initialization fails, set the engine to None and print a warning.
    # The speak_message function will check for this and avoid trying to use the engine.
    ENGINE = None
    print(f"Could not initialize TTS engine: {e}")


def notify_user(title: str, message: str):
    """
    Displays a standard desktop notification using the plyer library.

    Plyer is a platform-independent API to use features commonly available on
    desktop and mobile platforms. This function abstracts the OS-specific details
    of showing a notification.

    Args:
        title: The title of the notification window.
        message: The main content (body) of the notification.
    """
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="DocuMental",
            # The notification will automatically disappear after this many seconds.
            timeout=10,
        )
        print(f"Desktop notification sent: '{title}' ")
    except NotImplementedError:
        # This occurs if plyer does not support notifications on the current OS.
        print("Desktop notifications not supported on this system.")
    except Exception as e:
        # Fallback for any other unexpected errors from the plyer library.
        # We print the notification to the console so the message is not lost.
        print(f"Error sending desktop notification: {e}")
        print(f"Title: {title} Message: {message}")


def speak_message(message: str):
    """
    Uses the globally initialized TTS engine to speak the given message aloud.

    If the TTS engine failed to initialize, this function will simply print a
    message to the console indicating that speech is not available.

    Args:
        message: The text to be spoken.
    """
    # First, check if the engine was successfully initialized.
    if engine:
        try:
            print("Speaking message...")
            # Queue the text to be spoken.
            engine.say(message)
            # Block execution until all queued messages have been spoken.
            engine.runAndWait()
            print("Finished speaking.")
        except Exception as e:
            print(f"Error in TTS: {e}")
    else:
        # This is the fallback if the `engine` object is None.
        print("TTS engine not available.")


# --- Standalone Test Execution ---
if __name__ == "__main__":
    # This block allows the communication module to be tested independently
    # from the main application. Running `python communication.py` will execute this.
    print("--- Testing Communication Channels ---")

    # Test the desktop notification.
    TEST_TITLE = "Test Notification"
    TEST_MESSAGE = "If you see this, the visual notification is working."
    print("1. Testing Desktop Notification...")
    notify_user(TEST_TITLE, TEST_MESSAGE)

    # Test the text-to-speech output.
    SOPKEN_MESSAGE = "And if you can hear this, the audio is working."
    print("2. Testing Text-to-Speech...")
    speak_message(SOPKEN_MESSAGE)

    print("--- Test Complete ---")
    # sys.exit() is called to ensure the script terminates cleanly, especially
    # if the TTS engine has background threads.
    sys.exit()
