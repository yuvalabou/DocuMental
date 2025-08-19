"""
# The Brain Module: The Seat of Consciousness (Debug Version)

This module is where the magic happens. It takes a dry, technical event string
from the monitor, combines it with the printer's established personality, and
consults the local Large Language Model (LLM) to form a thought.
"""

import requests
import json
import time
from requests.exceptions import ConnectionError, HTTPError, Timeout
from .const import LM_STUDIO_ENDPOINT, Colors
from .personality import SYSTEM_PROMPT

# --- Configuration ---
# Maximum number of times to retry connecting to the LLM server.
MAX_RETRIES = 3
# Delay in seconds between retries.
RETRY_DELAY = 1


def get_llm_response(event_string: str) -> str:
    """
    Generates a human-readable message from a printer event string by querying a local LLM.

    This function performs two main operations:
    1.  It first queries the LLM server to get the ID of the currently loaded model.
        This makes the system flexible, as the user doesn't need to hardcode the model name.
    2.  It then sends the actual prompt (a combination of the system personality and the
        specific printer event) to the LLM's chat completions endpoint.

    Both operations include a retry mechanism to handle cases where the LLM server
    might be slow to start up or temporarily unavailable.

    Args:
        event_string: A detailed, human-readable string describing the printer event.

    Returns:
        A string containing the LLM's generated response, or an error message if the
        process fails.
    """
    print(f"{Colors.CYAN}--- Brain Module Invoked ---{Colors.RESET}")

    # --- Step 1: Get the available model name from the server with retries ---
    model_name = None
    for attempt in range(MAX_RETRIES):
        try:
            print(f"Attempt {attempt + 1}/{MAX_RETRIES}: Querying for models at: {LM_STUDIO_ENDPOINT}/models")
            # Request the list of available models from the server.
            model_response = requests.get(f"{LM_STUDIO_ENDPOINT}/models", timeout=10)
            model_response.raise_for_status()  # Raise an exception for bad status codes (4xx or 5xx).
            model_data = model_response.json()

            # Extract the model ID from the response. We assume the first model is the one to use.
            model_name = model_data.get("data", [{}])[0].get("id")
            if not model_name:
                return "Error: Could not determine the model name from LLM server. No model ID found."
            print(f"Using model: {model_name}")
            break  # If successful, exit the retry loop.

        # --- Exception Handling for Model Discovery ---
        except ConnectionError:
            error_message = "Error: Could not connect to LLM server. Is it running?"
        except HTTPError as e:
            error_message = f"Error: LLM server returned status {e.response.status_code}. Check server logs."
        except Timeout:
            error_message = "Error: LLM model list request timed out."
        except (IndexError, KeyError) as e:
            # This handles cases where the JSON response is not in the expected format.
            error_message = f"Error parsing model list from LLM server: {e}. Response: {model_response.text if 'model_response' in locals() else 'No response'}"
        except requests.exceptions.RequestException as e:
            error_message = f"An unexpected error occurred connecting to LLM server: {e}"

        # If an error occurred, print it and decide whether to retry.
        print(f"{Colors.RED}{error_message}{Colors.RESET}")
        if attempt < MAX_RETRIES - 1:
            print(f"Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
        else:
            # If all retries fail, return a final error message.
            return f"Error: Failed to get LLM model name after {MAX_RETRIES} attempts. {error_message}"

    # If model_name is still None after the loop, it means all attempts failed.
    if not model_name:
        return "Error: Failed to retrieve LLM model name."

    # --- Step 2: Construct the prompt for the LLM ---
    # The prompt consists of a system message (defining the personality) and a user message (the event).
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Translate the following event: '{event_string}'"},
    ]

    # --- Step 3: Send the prompt to the LLM server with retries ---
    for attempt in range(MAX_RETRIES):
        try:
            print(f"Attempt {attempt + 1}/{MAX_RETRIES}: Sending request to chat completions endpoint...")
            # Post the request to the chat completions endpoint.
            response = requests.post(
                f"{LM_STUDIO_ENDPOINT}/chat/completions",
                json={
                    "model": model_name,
                    "messages": messages,
                    "temperature": 0.7,  # Controls the creativity of the response.
                    "stream": False,     # We want the full response at once, not a stream.
                },
                timeout=20,  # A longer timeout for the generation itself.
            )
            response.raise_for_status()
            response_data = response.json()

            # --- Step 4: Extract and parse the response ---
            # The actual message is nested in the JSON response.
            raw_content = response_data["choices"][0]["message"]["content"].strip()

            # Some models wrap their responses in quotes or add prefixes.
            # This is a defensive measure to clean up the output.
            if '"' in raw_content:
                return raw_content.split('"')[1].strip()
            if ":" in raw_content:
                return raw_content.split(":")[-1].strip()

            return raw_content  # Return the cleaned-up response.

        # --- Exception Handling for Chat Completion ---
        except ConnectionError:
            error_message = "Error: Could not connect to LLM server. Is it running?"
        except HTTPError as e:
            error_message = f"Error: LLM server returned status {e.response.status_code}. Check server logs."
        except Timeout:
            error_message = "Error: LLM chat completion request timed out."
        except (KeyError, IndexError) as e:
            # Handles unexpected JSON structure from the server.
            error_message = f"Error parsing response from LLM server: {e}. Response: {response.text if 'response' in locals() else 'No response'}"
        except requests.exceptions.RequestException as e:
            error_message = f"An unexpected error occurred communicating with LLM server: {e}"

        # Print the error and decide whether to retry.
        print(f"{Colors.RED}{error_message}{Colors.RESET}")
        if attempt < MAX_RETRIES - 1:
            print(f"Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
        else:
            # If all retries fail, return a final error message.
            return f"Error: Failed to get LLM response after {MAX_RETRIES} attempts. {error_message}"

    # This line is reached if the loop completes without a successful response.
    return "Error: Failed to get LLM response after all retries."


if __name__ == "__main__":
    TEST_EVENT = "Job ID 124: Status change to 'ERROR' - Paper Jam"
    print(f"Testing with event: '{TEST_EVENT}'")
    llm_message = get_llm_response(TEST_EVENT)
    print(f"LLM Response: {llm_message}")
