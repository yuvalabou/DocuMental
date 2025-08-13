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

MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds


def get_llm_response(event_string: str) -> str:
    """
    Generates a human-readable message from a printer event string.
    """
    print(f"{Colors.CYAN}--- Brain Module Invoked ---{Colors.RESET}")

    model_name = None
    # 1. Get the available model name from the server with retries
    for attempt in range(MAX_RETRIES):
        try:
            print(f"Attempt {attempt + 1}/{MAX_RETRIES}: Querying for models at: {LM_STUDIO_ENDPOINT}/models")
            model_response = requests.get(f"{LM_STUDIO_ENDPOINT}/models", timeout=10)
            model_response.raise_for_status()  # Raise HTTPError for bad responses (4xx or 5xx)
            model_data = model_response.json()
            model_name = model_data.get("data", [{}])[0].get("id")
            if not model_name:
                return "Error: Could not determine the model name from LLM server. No model ID found."
            print(f"Using model: {model_name}")
            break  # Successfully got model name, exit retry loop
        except ConnectionError:
            error_message = "Error: Could not connect to LLM server. Is it running?"
        except HTTPError as e:
            error_message = f"Error: LLM server returned status {e.response.status_code}. Check server logs."
        except Timeout:
            error_message = "Error: LLM model list request timed out."
        except (IndexError, KeyError) as e:
            error_message = f"Error parsing model list from LLM server: {e}. Response: {model_response.text if 'model_response' in locals() else 'No response'}"
        except requests.exceptions.RequestException as e:
            error_message = f"Error connecting to LLM server: {e}"

        print(f"{Colors.RED}{error_message}{Colors.RESET}")
        if attempt < MAX_RETRIES - 1:
            print(f"Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
        else:
            return f"Error: Failed to get LLM model name after {MAX_RETRIES} attempts. {error_message}"

    if not model_name:
        return "Error: Failed to retrieve LLM model name."

    # 2. Construct the prompt
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Translate the following event: '{event_string}'"},
    ]

    # 3. Send the prompt to your LLM server with retries.
    for attempt in range(MAX_RETRIES):
        try:
            print(f"Attempt {attempt + 1}/{MAX_RETRIES}: Sending request to chat completions endpoint...")
            response = requests.post(
                f"{LM_STUDIO_ENDPOINT}/chat/completions",
                json={
                    "model": model_name,
                    "messages": messages,
                    "temperature": 0.7,
                    "stream": False,
                },
                timeout=20,
            )
            response.raise_for_status()
            response_data = response.json()

            # 4. Extract the raw response content.
            raw_content = response_data["choices"][0]["message"]["content"].strip()

            # 5. Defensively parse the response
            if '"' in raw_content:
                return raw_content.split('"')[1].strip()
            if ":" in raw_content:
                return raw_content.split(":")[-1].strip()

            return raw_content

        except ConnectionError:
            error_message = "Error: Could not connect to LLM server. Is it running?"
        except HTTPError as e:
            error_message = f"Error: LLM server returned status {e.response.status_code}. Check server logs."
        except Timeout:
            error_message = "Error: LLM chat completion request timed out."
        except (KeyError, IndexError) as e:
            error_message = f"Error parsing response from LLM server: {e}. Response: {response.text if 'response' in locals() else 'No response'}"
        except requests.exceptions.RequestException as e:
            error_message = f"Error communicating with LLM server: {e}"

        print(f"{Colors.RED}{error_message}{Colors.RESET}")
        if attempt < MAX_RETRIES - 1:
            print(f"Retrying in {RETRY_DELAY} seconds...")
            time.sleep(RETRY_DELAY)
        else:
            return f"Error: Failed to get LLM response after {MAX_RETRIES} attempts. {error_message}"

    return "Error: Failed to get LLM response."


if __name__ == "__main__":
    TEST_EVENT = "Job ID 124: Status change to 'ERROR' - Paper Jam"
    print(f"Testing with event: '{TEST_EVENT}'")
    llm_message = get_llm_response(TEST_EVENT)
    print(f"LLM Response: {llm_message}")
