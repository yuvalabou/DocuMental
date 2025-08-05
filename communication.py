"""
The Communication Module: The Mouthpiece

This module is the agent's voice. It takes a fully-formed thought (a title
and a message) and broadcasts it to the user's desktop, ensuring no act of
printing goes unnoticed or unjudged.
"""

import sys

from plyer import notification


def notify_user(title: str, message: str):
    """
    Displays a desktop notification.

    Args:
        title: The title of the notification.
        message: The main content of the notification.
    """
    # --- To be implemented ---
    # 1. Use plyer to display a desktop notification.
    #    - This is a simple function call.
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


if __name__ == '__main__':
    # This allows you to test the communication module independently.
    print("Testing desktop notification...")
    notify_user(
        "Test Notification",
        "If you see this, the communication module is working!"
    )
    print("Test complete.")
    sys.exit()
