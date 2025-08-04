
"""
The Communication Module

This module handles the final output. It's a simple, single-purpose function
that displays a desktop notification.
"""

from plyer import notification

def notify_user(title, message):
    """
    Displays a desktop notification.

    Args:
        title (str): The title of the notification.
        message (str): The main content of the notification.
    """
    # --- To be implemented ---
    # 1. Use plyer to display a desktop notification.
    #    - This is a simple function call.
    try:
        notification.notify(
            title=title,
            message=message,
            app_name="DocuMental",
            timeout=10  # Notification will disappear after 10 seconds
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
