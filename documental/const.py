"""
Constants and Configuration Module

This file serves as a single source of truth for all technical configuration
variables, static data, and constants used throughout the application.
Keeping them in one place makes the application easier to configure and maintain.
"""

# --- LLM Server Configuration ---
# The application loads its core configuration from an external JSON file.
# This allows users to change settings like the LLM server endpoint without editing the code.

# Maximum number of times to retry connecting to the LLM server.
MAX_RETRIES = 3
# Delay in seconds between retries.
RETRY_DELAY = 1

# A default endpoint is defined as a fallback in case the config file is missing or malformed.
DEFAULT_ENDPOINT = "http://localhost:1234/v1"


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
