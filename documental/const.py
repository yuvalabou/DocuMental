"""
Constants and Configuration Module

This file serves as a single source of truth for all technical configuration
variables, static data, and constants used throughout the application.
"""

import win32print

import json
import os

# --- Brain Module Constants ---
# Load configuration from config.json
CONFIG_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "config.json")
try:
    with open(CONFIG_FILE_PATH, "r") as f:
        config = json.load(f)
    LM_STUDIO_ENDPOINT = config["llm"]["lm_studio_endpoint"]
except FileNotFoundError:
    print(f"Error: config.json not found at {CONFIG_FILE_PATH}. Using default LM_STUDIO_ENDPOINT.")
    LM_STUDIO_ENDPOINT = "http://localhost:1234/v1"
except KeyError:
    print("Error: 'llm.lm_studio_endpoint' not found in config.json. Using default LM_STUDIO_ENDPOINT.")
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
