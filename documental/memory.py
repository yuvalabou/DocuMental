"""
# The Memory Module: The Agent's Long-Term Grudge Holder

This module provides the agent with a persistent memory, allowing it to
recall past print jobs, user habits, and document histories. It reads from
and writes to a simple JSON file (`memory.json`), enabling the agent to
generate more context-aware and personalized snark over time.
"""

import json
import os
from datetime import datetime
from .const import Colors

# Define the absolute path to the memory file, ensuring it's always located
# in the project root, regardless of where the script is run from.
MEMORY_FILE_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "memory.json"
)


def load_memory() -> dict:
    """
    Loads the memory data from the `memory.json` file.

    If the file doesn't exist (e.g., on first run) or if it contains corrupted
    JSON, it gracefully handles the error by returning a fresh, empty memory structure.

    Returns:
        A dictionary representing the agent's memory, typically with keys like "users" and "documents".
    """
    # If the memory file doesn't exist, return a default, empty structure.
    if not os.path.exists(MEMORY_FILE_PATH):
        return {"users": {}, "documents": {}}
    try:
        with open(MEMORY_FILE_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError) as e:
        # If the file is unreadable or not valid JSON, print a warning and start fresh.
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
    try:
        with open(MEMORY_FILE_PATH, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
    except IOError as e:
        # If the file cannot be written to (e.g., due to permissions), print an error.
        print(
            f"{Colors.RED}Error: Could not write to memory.json. Error: {e}{Colors.RESET}"
        )


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

    # Update user-specific memory
    if user_name != "N/A":
        # Get the existing user memory or create a new entry if it's their first time.
        user_memory = memory["users"].get(user_name, {"print_count": 0})
        user_memory["print_count"] += 1
        user_memory["last_print_timestamp"] = datetime.now().isoformat()
        memory["users"][user_name] = user_memory
        # Add a human-readable string to the context.
        context_parts.append(
            f"This is the {ordinal(user_memory['print_count'])} time '{user_name}' has printed."
        )

    # Update document-specific memory
    if doc_name != "N/A":
        # Get existing document memory or create a new one.
        doc_memory = memory["documents"].get(doc_name, {"print_count": 0})
        doc_memory["print_count"] += 1
        doc_memory["last_print_timestamp"] = datetime.now().isoformat()
        memory["documents"][doc_name] = doc_memory
        # Only add context if the document has been seen before to avoid redundancy.
        if doc_memory["print_count"] > 1:
            context_parts.append(
                f"The document '{doc_name}' has been printed {doc_memory['print_count']} times before."
            )

    # After updating the memory dictionary in place, save it back to the file.
    save_memory(memory)

    # Join the context parts into a single string and return it with the updated memory.
    return " ".join(context_parts), memory
