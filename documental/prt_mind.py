"""
DocuMental: The Main Orchestrator of Printer Discontent

This is the main script that ties all the modules together. It awakens the
agent, discovers all available printers, and runs an infinite loop to listen
for events, consult the brain, and broadcast the resulting snark to the user.
"""

import queue
import threading

import pythoncom
import win32print

from .brain import get_llm_response
from .communication import notify_user, speak_message
from .const import PRE_DEFINED_PATTERNS, Colors
from .memory import (
    get_context_without_updating,
    load_memory,
    update_and_get_context
    )
from .monitor import watch_printer_queue
from .utils import get_available_printers, get_job_status_string


def printer_monitoring_worker(printer_name: str, event_queue: queue.Queue):
    """
    A worker thread that monitors a single printer and puts events into a queue.
    It initializes COM for pywin32 to work correctly in a multi-threaded context.
    """
    try:
        pythoncom.CoInitialize()
        for event in watch_printer_queue(printer_name):
            # Check if the event is a dictionary and not an error string
            if isinstance(event, dict):
                event_queue.put((printer_name, event))
            else:
                # If it's a string, it's likely an error message from the monitor
                print(f"{Colors.RED}{event}{Colors.RESET}")
    except Exception as e:
        error_message = f"Error in monitor thread for '{printer_name}': {e}"
        print(f"{Colors.RED}{error_message}{Colors.RESET}")
        # We don't queue this error to avoid an infinite loop of processing it
    finally:
        pythoncom.CoUninitialize()


def format_event_for_llm(event_data: dict, memory_context: str) -> str:
    """Formats the job event data into a detailed string for the LLM."""
    event_type = event_data.get("event", "unknown_event")
    job_info = event_data.get("job_info", {})

    # Safely extract details with defaults
    doc_name = job_info.get("pDocument", "N/A")
    user_name = job_info.get("pUserName", "N/A")
    job_id = job_info.get("JobId", "N/A")
    status_code = job_info.get("Status", 0)
    status_str = get_job_status_string(status_code)
    total_pages = job_info.get("TotalPages", "N/A")
    size_kb = round(job_info.get("Size", 0) / 1024, 2)
    submitted_time = job_info.get("Submitted")
    if submitted_time:
        # Format pywintypes.datetime to a more readable string
        submitted_str = submitted_time.strftime("%Y-%m-%d %H:%M:%S")
    else:
        submitted_str = "N/A"

    # Detect keywords in the document name
    detected_keywords = [
        p for p in PRE_DEFINED_PATTERNS if p.lower() in doc_name.lower()
    ]
    keyword_str = (
        f"Detected keywords in document name: {', '.join(detected_keywords)}."
        if detected_keywords
        else ""
    )

    # Construct a detailed, human-readable string for the event
    base_event_str = ""
    if event_type == "new_job":
        base_event_str = (
            f"A new print job was submitted: "
            f"Document='{doc_name}', User='{user_name}', JobID={job_id}, "
            f"Pages={total_pages}, Size={size_kb} KB, Submitted='{submitted_str}', "
            f"InitialStatus='{status_str}'."
        )
    elif event_type == "status_change":
        base_event_str = (
            f"The status of a print job changed: "
            f"Document='{doc_name}', User='{user_name}', JobID={job_id}, "
            f"NewStatus='{status_str}', Pages={total_pages}, Size={size_kb} KB."
        )
    elif event_type == "job_deleted":
        base_event_str = (
            f"A print job was completed or removed: "
            f"Document='{doc_name}', User='{user_name}', JobID={job_id}."
        )
    else:
        base_event_str = f"An unknown event occurred: {event_data}"

    # Combine the base event, historical context, and keywords for the final prompt
    full_context = [base_event_str]
    if memory_context:
        full_context.append(f"Historical context: {memory_context}")
    if keyword_str:
        full_context.append(keyword_str)

    return " ".join(full_context)


def main():
    """The main function of the DocuMental application."""
    print(
        f"{Colors.BLUE}--- DocuMental: An Intelligent Printer Agent ---{Colors.RESET}"
    )

    try:
        printers_to_monitor = get_available_printers()
        if not printers_to_monitor:
            print(
                f"{Colors.RED}Error: No printers found on this system. Exiting.{Colors.RESET}"
            )
            return
    except Exception as e:
        print(f"{Colors.RED}Error fetching printers: {e}{Colors.RESET}")
        return

    print(f"\n{Colors.GREEN}DocuMental is now running...{Colors.RESET}")
    print(
        f"Monitoring all available printers: {Colors.CYAN}{', '.join(printers_to_monitor)}{Colors.RESET} (Press Ctrl+C to stop)"
    )
    print("-" * 50)

    # Load the persistent memory at startup
    memory_data = load_memory()

    # --- State Tracking for Notification Debouncing ---
    # A set to keep track of job IDs that have already been processed.
    processed_jobs = set()
    # A set of statuses that are important enough to warrant a notification even
    # if we have already notified about the job once.
    HIGH_PRIORITY_STATUSES = {
        win32print.JOB_STATUS_ERROR,
        win32print.JOB_STATUS_PAPEROUT,
        win32print.JOB_STATUS_USER_INTERVENTION,
        win32print.JOB_STATUS_BLOCKED_DEVQ,
    }

    event_queue = queue.Queue()
    threads = []

    for printer_name in printers_to_monitor:
        thread = threading.Thread(
            target=printer_monitoring_worker,
            args=(printer_name, event_queue),
            daemon=True,
        )
        threads.append(thread)
        thread.start()

    try:
        while True:
            try:
                printer_name, event_data = event_queue.get(timeout=1)

                if not isinstance(event_data, dict):
                    print(
                        f"{Colors.YELLOW}Received non-dict event: {event_data}{Colors.RESET}"
                    )
                    continue

                job_info = event_data.get("job_info", {})
                job_id = job_info.get("JobId")
                status_code = job_info.get("Status", 0)

                # --- Smart Notification Logic ---
                # Decide whether to process the event or ignore it to prevent spam.
                if job_id in processed_jobs:
                    # If we've seen this job, only notify for high-priority events.
                    is_high_priority = any(
                        status_code & status for status in HIGH_PRIORITY_STATUSES
                    )
                    if not is_high_priority:
                        continue  # Skip low-priority updates for already-seen jobs
                else:
                    # If it's a new job, mark it as processed.
                    processed_jobs.add(job_id)

                print(
                    f"{Colors.MAGENTA}Detected Event on '{printer_name}':{Colors.RESET} "
                    f"{event_data.get('event')} for doc '{job_info.get('pDocument', 'N/A')}'"
                )

                # Update memory only for new jobs to avoid duplicate counting.
                event_type = event_data.get("event")
                memory_context = ""
                if event_type == "new_job":
                    memory_context, memory_data = update_and_get_context(
                        job_info, memory_data
                    )
                else:
                    memory_context = get_context_without_updating(job_info, memory_data)

                # Format the rich event data into a string for the LLM
                event_string_for_llm = format_event_for_llm(event_data, memory_context)

                # print(f"{Colors.YELLOW}--- Sending to LLM: ---\n{event_string_for_llm}{Colors.RESET}")

                llm_message = get_llm_response(event_string_for_llm)

                if llm_message.startswith("Error:"):
                    print(f"{Colors.RED}{llm_message}{Colors.RESET}")
                    continue  # Skip to the next event

                print(f'{Colors.BLUE}LLM Response:{Colors.RESET} "{llm_message}" ')

                # --- Dispatch Notifications ---
                notify_user(f"Printer Alert: {printer_name}", llm_message)
                speak_message(llm_message)

                print("-" * 50)

            except queue.Empty:
                continue
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Monitoring stopped by user. Goodbye!{Colors.RESET}")


if __name__ == "__main__":
    main()
