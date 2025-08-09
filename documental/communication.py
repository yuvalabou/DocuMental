"""
The Communication Module: The Mouthpiece

This module is the agent's voice. It provides distinct channels for visual
and auditory notifications, allowing the user to see and/or hear what the
printer is thinking.
"""

import sys

import pyttsx3
from plyer import notification

# Initialize the TTS engine globally to avoid re-initializing it on every call
try:
    engine = pyttsx3.init()
except Exception as e:
    engine = None
    print(f"Could not initialize TTS engine: {e}")


def notify_user(title: str, message: str):
    """
    Displays a desktop notification.

    Args:
        title: The title of the notification.
        message: The main content of the notification.
    """
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="DocuMental",
            timeout=10,  # Notification will disappear after defined seconds
        )
        print(f"Desktop notification sent: '{title}'")
    except NotImplementedError:
        print("Desktop notifications not supported on this system.")
    except Exception as e:
        # If plyer fails, just print to console.
        print(f"Error sending desktop notification: {e}")
        print(f"Title: {title}\nMessage: {message}")


def speak_message(message: str):
    """
    Uses the TTS engine to speak the given message aloud.

    Args:
        message: The text to be spoken.
    """
    if engine:
        try:
            print("Speaking message...")
            engine.say(message)
            engine.runAndWait()
            print("Finished speaking.")
        except Exception as e:
            print(f"Error in TTS: {e}")
    else:
        print("TTS engine not available.")


if __name__ == "__main__":
    # This allows you to test the communication module independently.
    print("--- Testing Communication Channels ---")

    test_title = "Test Notification"
    test_message = "If you see this, the visual notification is working."
    print(f"\n1. Testing Desktop Notification...")
    notify_user(test_title, test_message)

    spoken_message = "And if you can hear this, the audio is working."
    print(f"\n2. Testing Text-to-Speech...")
    speak_message(spoken_message)

    print("\n--- Test Complete ---")
    sys.exit()
