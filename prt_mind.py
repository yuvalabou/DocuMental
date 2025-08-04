"""
DocuMental: The Main Orchestrator of Printer Discontent

This is the main script that ties all the modules together. It awakens the
agent, asks it which printer to haunt, and then runs an infinite loop to
listen for printer events, consult the brain, and broadcast the resulting
snark to the user.
"""

import time

from brain import get_llm_response
from communication import notify_user
from monitor import watch_printer_queue, get_available_printers
from const import Colors


def main():
    """
    The main function of the DocuMental application.
    """
    print(f"{Colors.BLUE}--- DocuMental: An Intelligent Printer Agent ---{Colors.RESET}")

    # 1. Dynamically get the list of available printers.
    try:
        printers = get_available_printers()
        if not printers:
            print(f"{Colors.RED}Error: No printers found on this system. Exiting.{Colors.RESET}")
            return
    except Exception as e:
        print(f"{Colors.RED}Error fetching printers: {e}{Colors.RESET}")
        return

    # 2. Ask the user to choose a printer.
    print(f"{Colors.YELLOW}Available printers:{Colors.RESET}")
    for i, printer_name in enumerate(printers):
        print(f"  {Colors.CYAN}[{i}]{Colors.RESET} {printer_name}")
    
    try:
        choice = int(input(f"\nEnter the number of the printer you want to monitor: "))
        if not 0 <= choice < len(printers):
            print(f"{Colors.RED}Invalid choice. Exiting.{Colors.RESET}")
            return
        chosen_printer = printers[choice]
    except (ValueError, IndexError):
        print(f"{Colors.RED}Invalid input. Please enter a number from the list. Exiting.{Colors.RESET}")
        return

    print(f"\n{Colors.GREEN}DocuMental is now running...{Colors.RESET}")
    print(f"Monitoring printer: {Colors.CYAN}'{chosen_printer}'{Colors.RESET} (Press Ctrl+C to stop)")
    print("-" * 50)

    # 3. The main loop iterates over events from the chosen printer.
    try:
        for event in watch_printer_queue(chosen_printer):
            print(f"{Colors.MAGENTA}Detected Event:{Colors.RESET} {event}")

            # Pass the event to the Brain Module.
            llm_message = get_llm_response(event)
            print(f"{Colors.BLUE}LLM Response:{Colors.RESET} \"{llm_message}\" ")

            # Pass the LLM's response to the Communication Module.
            notify_user(f"Printer Alert: {chosen_printer}", llm_message)
            print("-" * 50)
    except KeyboardInterrupt:
        print(f"\n{Colors.YELLOW}Monitoring stopped by user. Goodbye!{Colors.RESET}")



if __name__ == "__main__":
    main()
