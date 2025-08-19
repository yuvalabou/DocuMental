"""
The Memory Module: The Agent's Long-Term Grudge Holder

This module provides the agent with a persistent memory, allowing it to
recall past print jobs, user habits, and document histories. It reads from
and writes to a simple JSON file (`memory.json`), enabling the agent to
generate more context-aware and personalized snark over time.
"""

import json
import os
from datetime import datetime

from .const import Colors
from .utils import ordinal

# Define the absolute path to the memory file, ensuring it's always located
# in the project root, regardless of where the script is run from.
MEMORY_FILE_PATH = os.path.join(os.getcwd(), "memory.json")


def load_memory() -> dict:
    """
    Loads the memory data from the `memory.json` file.

    If the file doesn't exist (e.g., on first run) or if it contains corrupted
    JSON, it gracefully handles the error by returning a fresh, empty memory structure.

    Returns:
        A dictionary representing the agent's memory, typically with keys like "users" and "documents".
    """
    if not os.path.exists(MEMORY_FILE_PATH):
        print(
            f"{Colors.YELLOW}Memory file not found. Creating a new one at {MEMORY_FILE_PATH}.{Colors.RESET}"
        )
        default_memory = {"users": {}, "documents": {}}
        save_memory(default_memory)
        return default_memory
    try:
        with open(MEMORY_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        print(
            f"{Colors.YELLOW}Warning: Could not read or parse memory.json. Starting with a fresh memory. Error: {e}{Colors.RESET}"
        )
        return {"users": {}, "documents": {}}


def save_memory(data: dict):
    """
    Saves the provided memory dictionary to the `memory.json` file.

    The data is written in a pretty-printed JSON format (with indentation)
    to make it human-readable for debugging or manual inspection.

    Args:
        data: The dictionary containing the memory data to be saved.
    """
    print(f"{Colors.YELLOW}--- Attempting to save memory ---")
    print(f"Target file path: {MEMORY_FILE_PATH}")
    print(f"Data to save: {data}")
    try:
        with open(MEMORY_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        print(f"{Colors.GREEN}--- Memory saved successfully ---")
    except IOError as e:
        print(f"--- CRITICAL: FAILED TO SAVE MEMORY ---")
        print(f"Error: Could not write to memory.json. Error: {e}")
        print(f"Please check file permissions for the directory: {os.path.dirname(MEMORY_FILE_PATH)}")
        print(f"--- END OF ERROR ---")


def update_and_get_context(job_info: dict, memory: dict) -> tuple[str, dict]:
    """
    Updates the memory with details from a new print job and generates a historical context string.

    This function is the core of the memory system. It takes the current job, updates the
    print counts for the user and the document, and then creates a natural language
    string summarizing this history for the LLM.

    Args:
        job_info: A dictionary containing details about the current print job.
        memory: The current memory data dictionary, loaded at the start of the application.

    Returns:
        A tuple containing:
        - A string with the historical context (e.g., "This is the 3rd time 'user' has printed.").
        - The updated memory dictionary.
    """
    user_name = job_info.get("pUserName", "N/A")
    doc_name = job_info.get("pDocument", "N/A")
    context_parts = []

    if user_name != "N/A":
        user_memory = memory["users"].get(user_name, {"print_count": 0})
        user_memory["print_count"] += 1
        user_memory["last_print_timestamp"] = datetime.now().isoformat()
        memory["users"][user_name] = user_memory
        context_parts.append(
            f"This is the {ordinal(user_memory['print_count'])} time '{user_name}' has printed."
        )

    if doc_name != "N/A":
        doc_memory = memory["documents"].get(doc_name, {"print_count": 0})
        doc_memory["print_count"] += 1
        doc_memory["last_print_timestamp"] = datetime.now().isoformat()
        memory["documents"][doc_name] = doc_memory
        if doc_memory["print_count"] > 1:
            context_parts.append(
                f"The document '{doc_name}' has been printed {doc_memory['print_count']} times before."
            )

    save_memory(memory)

    return " ".join(context_parts), memory


def get_context_without_updating(job_info: dict, memory: dict) -> str:
    """
    Generates a historical context string without modifying the memory.

    This is a read-only operation used for events like status changes, where we
    want to provide context to the LLM without incrementing print counts.

    Args:
        job_info: A dictionary containing details about the current print job.
        memory: The current memory data dictionary.

    Returns:
        A string with the historical context.
    """
    user_name = job_info.get("pUserName", "N/A")
    doc_name = job_info.get("pDocument", "N/A")
    context_parts = []

    if user_name != "N/A" and user_name in memory["users"]:
        user_memory = memory["users"][user_name]
        context_parts.append(
            f"This is the {ordinal(user_memory['print_count'])} time '{user_name}' has printed."
        )

    if doc_name != "N/A" and doc_name in memory["documents"]:
        doc_memory = memory["documents"][doc_name]
        if doc_memory["print_count"] > 0:
            context_parts.append(
                f"The document '{doc_name}' has been printed {doc_memory['print_count']} times before."
            )

    return " ".join(context_parts)