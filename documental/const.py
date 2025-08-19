"""
# Constants and Configuration Module

This file serves as a single source of truth for all technical configuration
variables, static data, and constants used throughout the application.
Keeping them in one place makes the application easier to configure and maintain.
"""

import json
import os

# --- LLM Server Configuration ---
# The application loads its core configuration from an external JSON file.
# This allows users to change settings like the LLM server endpoint without editing the code.

# Construct the absolute path to `config.json`.
# It's expected to be in the project's root directory, one level above this file's directory.
CONFIG_FILE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "config.json"
)

# A default endpoint is defined as a fallback in case the config file is missing or malformed.
DEFAULT_ENDPOINT = "http://localhost:1234/v1"

try:
    with open(CONFIG_FILE_PATH, "r", encoding="utf-8") as f:
        config = json.load(f)
    # Safely get the endpoint from the nested JSON structure.
    LM_STUDIO_ENDPOINT = config.get("llm", {}).get(
        "lm_studio_endpoint", DEFAULT_ENDPOINT
    )
except (FileNotFoundError, json.JSONDecodeError) as e:
    print(
        f"Warning: Could not load or parse {CONFIG_FILE_PATH}. Using default endpoint. Error: {e}"
    )
    LM_STUDIO_ENDPOINT = DEFAULT_ENDPOINT


# --- Color Constants for Console Output ---
# This class uses ANSI escape codes to add color to console output, making it easier to read.
# For example, errors can be printed in red and success messages in green.
class Colors:
    RESET = "\033[0m"  # Resets the color to the default.
    RED = "\033[91m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BLUE = "\033[94m"
    MAGENTA = "\033[95m"
    CYAN = "\033[96m"


# --- Document Keyword Patterns ---
# This is a list of keywords that the agent will look for in document names.
# If a document name contains one of these keywords (case-insensitively),
# this information is passed to the LLM to generate a more specific and context-aware response.
# For example, seeing the word "resume" might prompt a snarky comment about job hunting.
PRE_DEFINED_PATTERNS: list[str] = [
    "netfabb",
    "resume",
    "confidential",
    "secret",
    "private",
    "invoice",
    "recipe",
    "vacation",
    "plans",
    "report",
    "draft",
]
