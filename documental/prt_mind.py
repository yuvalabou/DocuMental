"""
DocuMental: The Main Orchestrator of Printer Discontent

This is the main script that ties all the modules together. It awakens the
agent, asks it which printers to haunt, and then runs an infinite loop to
listen for printer events from multiple sources, consult the brain, and
broadcast the resulting snark to the user.
"""

import threading
import queue
import time

from brain import get_llm_response
from communication import notify_user
from const import Colors
from monitor import get_available_printers, watch_printer_queue


def printer_monitoring_worker(printer_name: str, event_queue: queue.Queue):
    """
    A worker thread that monitors a single printer and puts events into a queue.
    """
    try:
        for event in watch_printer_queue(printer_name):
            event_queue.put((printer_name, event))
    except Exception as e:
        # Log errors from the worker thread
        error_message = f"Error in monitor thread for '{printer_name}': {e}"
        print(f"{Colors.RED}{error_message}{Colors.RESET}")
        event_queue.put((printer_name, error_message))

def main():
    """
    The main function of the DocuMental application.
    """
    print(f"{Colors.BLUE}--- DocuMental: An Intelligent Printer Agent ---{Colors.RESET}")

    try:
        printers = get_available_printers()
        if not printers:
            print(f"{Colors.RED}Error: No printers found on this system. Exiting.{Colors.RESET}")
            return
    except Exception as e:
        print(f"{Colors.RED}Error fetching printers: {e}{Colors.RESET}")
        return

    print(f"{Colors.YELLOW}Available printers:{Colors.RESET}")
    for i, printer_name in enumerate(printers):
        print(f"  {Colors.CYAN}[{i}]{Colors.RESET} {printer_name}")

    try:
        choices_str = input(f"\nEnter the numbers of the printers to monitor (comma-separated, e.g., 0,2): ")
        chosen_indices = [int(c.strip()) for c in choices_str.split(',')]
        
        chosen_printers = []
        for i in chosen_indices:
            if 0 <= i < len(printers):
                chosen_printers.append(printers[i])
            else:
                print(f"{Colors.RED}Warning: Invalid printer index {i} ignored.{Colors.RESET}")

        if not chosen_printers:
            print(f"{Colors.RED}No valid printers selected. Exiting.{Colors.RESET}")
            return

    except (ValueError, IndexError):
        print(f"{Colors.RED}Invalid input. Please enter numbers from the list. Exiting.{Colors.RESET}")
        return

    print(f"\n{Colors.GREEN}DocuMental is now running...{Colors.RESET}")
    print(f"Monitoring printers: {Colors.CYAN}{', '.join(chosen_printers)}{Colors.RESET} (Press Ctrl+C to stop)")
    print("-" * 50)

    event_queue = queue.Queue()
    threads = []

    for printer_name in chosen_printers:
        thread = threading.Thread(target=printer_monitoring_worker, args=(printer_name, event_queue), daemon=True)
        threads.append(thread)
        thread.start()

    try:
        while True:
            try:
                printer_name, event = event_queue.get(timeout=1)  # Wait for 1 second
                print(f"{Colors.MAGENTA}Detected Event on '{printer_name}':{Colors.RESET} {event}")

                llm_message = get_llm_response(event)
                print(f"{Colors.BLUE}LLM Response:{Colors.RESET} \"{llm_message}\" ")

                notify_user(f"Printer Alert: {printer_name}", llm_message)
                print("-" * 50)
            except queue.Empty:
                # This allows the main loop to be responsive to KeyboardInterrupt
                continue
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Monitoring stopped by user. Goodbye!{Colors.RESET}")

if __name__ == "__main__":
    main()
