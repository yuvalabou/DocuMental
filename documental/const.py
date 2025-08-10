"""
Constants and Configuration Module

This file serves as a single source of truth for all technical configuration
variables, static data, and constants used throughout the application.
"""

import win32print

# --- Brain Module Constants ---
LM_STUDIO_ENDPOINT = "http://localhost:1234/v1"


# --- Color Constants (ANSI Escape Codes) ---
class Colors:
    RESET = "\033[0m"
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"


PRE_DEFINED_PATTERNS: list[str] = [
    "netfabb",
]
