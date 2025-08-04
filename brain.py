"""
The Brain Module

This module takes a structured event from the monitor and turns it into a
human-readable message using a local Large Language Model (LLM) via Ollama.
"""

import requests

def get_llm_response(event_string):
    """
    Generates a human-readable message from a printer event string.

    This function constructs a prompt for a local LLM, sends it to an Ollama
    server, and returns the LLM's response.

    Args:
        event_string (str): A structured string describing the printer event.
                            (e.g., "Job ID 124: Status change to 'ERROR' - Paper Jam")

    Returns:
        str: The LLM's generated response as a simple string.
             Returns an error message if the request fails.
    """
    # --- To be implemented ---
    # 1. Construct a prompt for the local LLM.
    #    - The prompt should provide context and ask the LLM to act as a
    #      helpful printer assistant.
    prompt = f"""
    Act as a helpful but slightly witty printer assistant.
    A printer just reported the following event: '{event_string}'.
    Translate this technical event into a short, user-friendly notification
    (less than 25 words).
    """

    # 2. Send the prompt to your local Ollama server.
    #    - Define the Ollama endpoint and the model to use.
    ollama_endpoint = "http://localhost:11434/api/generate"
    model_name = "phi-3-mini" # Make sure you have pulled this model with `ollama pull phi-3-mini`

    try:
        response = requests.post(
            ollama_endpoint,
            json={
                "model": model_name,
                "prompt": prompt,
                "stream": False, # We want the full response at once
            },
            timeout=20 # 20 seconds timeout
        )
        response.raise_for_status() # Raise an exception for bad status codes (4xx or 5xx)

        # 3. Return the LLM's response as a simple string.
        return response.json().get("response", "No response content from LLM.").strip()

    except requests.exceptions.RequestException as e:
        return f"Error communicating with Ollama: {e}"


if __name__ == '__main__':
    # This allows you to test the brain module independently.
    # Make sure your Ollama server is running.
    TEST_EVENT = "Job ID 124: Status change to 'ERROR' - Paper Jam"
    print(f"Testing with event: '{TEST_EVENT}'")
    llm_message = get_llm_response(TEST_EVENT)
    print(f"LLM Response: {llm_message}")
