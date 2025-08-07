"""
# The Brain Module: The Seat of Consciousness (Debug Version)

This module is where the magic happens. It takes a dry, technical event string
from the monitor, combines it with the printer's established personality, and
consults the local Large Language Model (LLM) to form a thought.
"""

import requests
import json
from const import LM_STUDIO_ENDPOINT, Colors
from personality import SYSTEM_PROMPT

def get_llm_response(event_string: str) -> str:
    """
    Generates a human-readable message from a printer event string.
    """
    print(f"{Colors.CYAN}--- Brain Module Invoked ---{Colors.RESET}")
    # 1. Get the available model name from the server
    try:
        print(f"Querying for models at: {LM_STUDIO_ENDPOINT}/models")
        model_response = requests.get(f"{LM_STUDIO_ENDPOINT}/models", timeout=10)
        model_response.raise_for_status()
        model_data = model_response.json()
        print(f"Received model data: {json.dumps(model_data, indent=2)}")
        model_name = model_data.get("data", [{}])[0].get("id")
        if not model_name:
            return "Error: Could not determine the model name from LM Studio."
        print(f"Using model: {model_name}")
    except requests.exceptions.RequestException as e:
        return f"Error connecting to LM Studio to get model list: {e}"
    except (IndexError, KeyError) as e:
        return f"Error parsing model list from LM Studio: {e}"

    # 2. Construct the prompt
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": f"Translate the following event: '{event_string}'"}
    ]
    print(f"Constructed prompt: {json.dumps(messages, indent=2)}")

    # 3. Send the prompt to your LM Studio server.
    try:
        print("Sending request to chat completions endpoint...")
        response = requests.post(
            f"{LM_STUDIO_ENDPOINT}/chat/completions",
            json={
                "model": model_name,
                "messages": messages,
                "temperature": 0.7,
                "stream": False,
            },
            timeout=20
        )
        response.raise_for_status()
        response_data = response.json()
        print(f"Received response: {json.dumps(response_data, indent=2)}")

        # 4. Extract the raw response content.
        raw_content = response_data['choices'][0]['message']['content'].strip()

        # 5. Defensively parse the response
        if '"' in raw_content:
            return raw_content.split('"')[1].strip()
        if ':' in raw_content:
            return raw_content.split(':')[-1].strip()

        return raw_content

    except requests.exceptions.RequestException as e:
        return f"Error communicating with LM Studio: {e}"
    except (KeyError, IndexError) as e:
        return f"Error parsing response from LM Studio: {e}. Response: {response.text}"

if __name__ == '__main__':
    TEST_EVENT = "Job ID 124: Status change to 'ERROR' - Paper Jam"
    print(f"Testing with event: '{TEST_EVENT}'")
    llm_message = get_llm_response(TEST_EVENT)
    print(f"LLM Response: {llm_message}")