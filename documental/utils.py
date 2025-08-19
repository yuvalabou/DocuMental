"""
Utilities and Helpers Module

This file contains miscellaneous helper functions used across the application,
such as configuration management, string formatting, and system interactions.
Keeping them here avoids cluttering the main logic modules.
"""

import json
import os

import win32print

from .const import DEFAULT_ENDPOINT, Colors

# It's better to define the path to the config file here, as this is the module
# responsible for reading and creating it.
CONFIG_FILE_PATH = os.path.join(os.getcwd(), "config.json")


def load_or_create_config() -> dict:
    """
    Loads the `config.json` file or creates it with default values if it doesn't exist.

    This function centralizes the configuration logic, ensuring that the application
    always has a valid configuration to work with.

    Returns:
        A dictionary containing the application's configuration.
    """
    try:
        with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        print(
            f"{Colors.YELLOW}Warning: {CONFIG_FILE_PATH} not found. Creating it with default values.{Colors.RESET}"
        )
        default_config = {"llm": {"lm_studio_endpoint": DEFAULT_ENDPOINT}}
        try:
            with open(CONFIG_FILE_PATH, "w", encoding="utf-8") as f:
                json.dump(default_config, f, indent=4)
            return default_config
        except IOError as write_error:
            print(
                f"{Colors.RED}Error: Could not write to {CONFIG_FILE_PATH}. Error: {write_error}{Colors.RESET}"
            )
            # Return the default config in-memory even if file write fails
            return default_config
    except json.JSONDecodeError as e:
        print(
            f"{Colors.YELLOW}Warning: Could not parse {CONFIG_FILE_PATH}. Using default endpoint. Error: {e}{Colors.RESET}"
        )
        # Return a default config structure if the file is corrupted
        return {"llm": {"lm_studio_endpoint": DEFAULT_ENDPOINT}}


def ordinal(n: int) -> str:
    """
    Converts an integer into its ordinal representation (e.g., 1 -> "1st", 2 -> "2nd").
    This is a utility function to make the historical context more human-readable.
    """
    # Handles the special cases for 11th, 12th, 13th
    if 11 <= (n % 100) <= 13:
        suffix = "th"
    else:
        # Handles all other cases (1st, 2nd, 3rd, 4th, etc.)
        suffix = ["th", "st", "nd", "rd", "th"][min(n % 10, 4)]
    return str(n) + suffix


def get_available_printers() -> list:
    """Returns a list of all installed printer names."""
    try:
        printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL, None, 1)
        return [printer[2] for printer in printers]
    except Exception:
        return []


def get_job_status_string(status_code: int) -> str:
    """Converts a status code into a descriptive string."""
    status_map = {
        win32print.JOB_STATUS_PAUSED: "Paused",
        win32print.JOB_STATUS_ERROR: "Error",
        win32print.JOB_STATUS_DELETING: "Deleting",
        win32print.JOB_STATUS_SPOOLING: "Spooling",
        win32print.JOB_STATUS_PRINTING: "Printing",
        win32print.JOB_STATUS_OFFLINE: "Offline",
        win32print.JOB_STATUS_PAPEROUT: "Paper Out",
        win32print.JOB_STATUS_PRINTED: "Printed",
        win32print.JOB_STATUS_DELETED: "Deleted",
        win32print.JOB_STATUS_BLOCKED_DEVQ: "Blocked",
        win32print.JOB_STATUS_USER_INTERVENTION: "User Intervention",
    }
    for status, text in status_map.items():
        if status_code & status:
            return text
    return f"Unknown Status ({status_code})"