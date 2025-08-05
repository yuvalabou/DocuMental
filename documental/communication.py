"""
The Communication Module: The Mouthpiece

This module is the agent's voice. It takes a fully-formed thought (a title
and a message) and broadcasts it to the user's desktop, ensuring no act of
printing goes unnoticed or unjudged.
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


def speak_message(message: str):
    """
    Uses the TTS engine to speak the given message.
    """
    if engine:
        try:
            engine.say(message)
            engine.runAndWait()
        except Exception as e:
            print(f"Error in TTS: {e}")

def notify_user(title: str, message: str):
    """
    Displays a desktop notification and speaks the message.

    Args:
        title: The title of the notification.
        message: The main content of the notification.
    """
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="DocuMental",
            timeout=5  # Notification will disappear after defined seconds
        )
        print(f"Notification sent: '{title}'")
    except Exception as e:
        # If plyer fails, just print to console.
        print(f"Error sending notification: {e}")
        print(f"Title: {title}\nMessage: {message}")

    # Speak the message aloud.
    speak_message(message)


if __name__ == '__main__':
    # This allows you to test the communication module independently.
    print("Testing desktop notification and TTS...")
    notify_user(
        "Test Notification",
        "If you see this and hear me, the communication module is working!"
    )
    print("Test complete.")
    sys.exit()
