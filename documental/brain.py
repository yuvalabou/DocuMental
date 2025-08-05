"""
The Brain Module: The Seat of Consciousness

This module is where the magic happens. It takes a dry, technical event string
from the monitor, combines it with the printer's established personality, and
consults the local Large Language Model (LLM) to form a thought.

It's responsible for connecting to the LLM server, dynamically figuring out
which model to talk to, and cleaning up the LLM's response to ensure it's just
the witty notification and not a rambling monologue.
"""

import requests

from const import LM_STUDIO_ENDPOINT
from personality import SYSTEM_PROMPT


def get_llm_response(event_string: str) -> str:
    """
    Generates a human-readable message from a printer event string.

    This function constructs a prompt for a local LLM, sends it to an Ollama
    server, and returns the LLM's response.
    """
    # 1. Get the available model name from the server
    try:
        model_response = requests.get(f"{LM_STUDIO_ENDPOINT}/models", timeout=10)
        model_response.raise_for_status()
        model_name = model_response.json().get("data", [{}])[0].get("id")
        if not model_name:
            return "Error: Could not determine the model name from LM Studio."
    except requests.exceptions.RequestException as e:
        return f"Error connecting to LM Studio to get model list: {e}"
    except IndexError:
        return "Error: No models available in LM Studio."

    # 2. Construct the prompt in the OpenAI chat format.
    #    - The "system" message sets the personality and, crucially, the output format.
    #    - The "user" message provides the specific, real-time event.
    messages = [
        {
            "role": "system",
            "content": SYSTEM_PROMPT
        },
        {
            "role": "user",
            "content": f"Translate the following event: '{event_string}'"
        }
    ]

    # 3. Send the prompt to your LM Studio server.
    try:
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

        # 4. Extract the raw response content.
        raw_content = response.json()['choices'][0]['message']['content'].strip()

        # 5. Defensively parse the response to remove "thinking" steps.
        #    - This looks for common conversational markers like "Here's the notification:"
        #      or quotation marks and extracts only the final message.
        if '"' in raw_content:
            # Extract content within the first pair of double quotes
            return raw_content.split('"')[1].strip()
        if ':' in raw_content:
            # Take the part after the last colon, assuming it's the final message
            return raw_content.split(':')[-1].strip()

        # If no special markers are found, return the cleaned-up raw content
        return raw_content

    except requests.exceptions.RequestException as e:
        return f"Error communicating with LM Studio: {e}"
    except (KeyError, IndexError) as e:
        return f"Error parsing response from LM Studio: {e}. Response: {response.text}"


if __name__ == '__main__':
    # This allows you to test the brain module independently.
    # Make sure your Ollama server is running.
    TEST_EVENT = "Job ID 124: Status change to 'ERROR' - Paper Jam"
    print(f"Testing with event: '{TEST_EVENT}'")
    llm_message = get_llm_response(TEST_EVENT)
    print(f"LLM Response: {llm_message}")
