DocuMental: The Main Orchestrator of Printer Discontent

This is the main script that ties all the modules together. It awakens the
agent, discovers all available printers, and runs an infinite loop to listen
for events, consult the brain, and broadcast the resulting snark to the user.


import threading
import queue
import time

from brain import get_llm_response
from communication import notify_user, speak_message
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
        error_message = f"Error in monitor thread for '{printer_name}': {e}"
        print(f"{Colors.RED}{error_message}{Colors.RESET}")
        event_queue.put((printer_name, error_message))

def main():
    """
    The main function of the DocuMental application.
    """
    print(f"{Colors.BLUE}--- DocuMental: An Intelligent Printer Agent ---{Colors.RESET}")

    try:
        printers_to_monitor = get_available_printers()
        if not printers_to_monitor:
            print(f"{Colors.RED}Error: No printers found on this system. Exiting.{Colors.RESET}")
            return
    except Exception as e:
        print(f"{Colors.RED}Error fetching printers: {e}{Colors.RESET}")
        return

    print(f"\n{Colors.GREEN}DocuMental is now running...{Colors.RESET}")
    print(f"Monitoring all available printers: {Colors.CYAN}{', '.join(printers_to_monitor)}{Colors.RESET} (Press Ctrl+C to stop)")
    print("-" * 50)

    event_queue = queue.Queue()
    threads = []

    for printer_name in printers_to_monitor:
        thread = threading.Thread(target=printer_monitoring_worker, args=(printer_name, event_queue), daemon=True)
        threads.append(thread)
        thread.start()

    try:
        while True:
            try:
                printer_name, event = event_queue.get(timeout=1)
                print(f"{Colors.MAGENTA}Detected Event on '{printer_name}':{Colors.RESET} {event}")

                llm_message = get_llm_response(event)
                print(f"{Colors.BLUE}LLM Response:{Colors.RESET} \"{llm_message}\" ")

                # --- Dispatch Notifications ---
                # 1. Visual desktop notification
                notify_user(f"Printer Alert: {printer_name}", llm_message)
                
                # 2. Spoken audio notification
                speak_message(llm_message)
                
                print("-" * 50)

            except queue.Empty:
                continue
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Monitoring stopped by user. Goodbye!{Colors.RESET}")

if __name__ == "__main__":
    main()
