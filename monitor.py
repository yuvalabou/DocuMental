"""
The Monitor Module: The Eyes and Ears

This script is the agent's connection to the physical world. It does one thing:
it spies on the Windows printer queue, translates the cryptic machine language
of status codes, and reports any activity—no matter how mundane—as a
structured event. It is the source of all office gossip.
"""

import time
import win32print
import pywintypes

from const import JOB_STATUS_MAP, Colors


def get_available_printers() -> list:
    """Returns a list of all installed printer names."""
    printers = win32print.EnumPrinters(win32print.PRINTER_ENUM_LOCAL, None, 1)
    return [printer[2] for printer in printers]

def get_job_status_string(status_code):
    """Converts a status code into a descriptive string."""
    return JOB_STATUS_MAP.get(status_code, f"Unknown Status ({status_code})")

def watch_printer_queue(printer_name: str):
    """
    Monitors a specified printer queue and yields event strings for any changes.

    Args:
        printer_name (str): The name of the printer to monitor.

    Yields:
        str: A formatted string describing the printer event.
    """
    print(f"Starting to monitor printer: {printer_name}")
    last_jobs = {}
    printer_handle = win32print.OpenPrinter(printer_name)

    try:
        while True:
            try:
                current_jobs_info = win32print.EnumJobs(printer_handle, 0, -1, 2)
                current_jobs = {job['JobId']: job for job in current_jobs_info}

                # Check for new jobs or status changes
                for job_id, job in current_jobs.items():
                    status_str = get_job_status_string(job['Status'])
                    if job_id not in last_jobs:
                        yield f"Job ID {job_id}: New job, '{job['pDocument']}' with status '{status_str}'"
                    elif job['Status'] != last_jobs[job_id]['Status']:
                        yield f"Job ID {job_id}: Status change to '{status_str}' for document '{job['pDocument']}'"

                # Check for completed or deleted jobs
                for job_id in list(last_jobs.keys()):
                    if job_id not in current_jobs:
                        yield f"Job ID {job_id}: Job '{last_jobs[job_id]['pDocument']}' completed or removed."

                last_jobs = current_jobs
            except pywintypes.error as e:
                yield f"{Colors.RED}Error connecting to printer: {e}. Retrying...{Colors.RESET}"
            
            time.sleep(5)
    finally:
        win32print.ClosePrinter(printer_handle)

if __name__ == '__main__':
    # This allows you to run the monitor independently for testing.
    print(f"{Colors.BLUE}Available printers:{Colors.RESET}")
    printers = get_available_printers()
    for i, p_name in enumerate(printers):
        print(f"  {Colors.CYAN}[{i}]{Colors.RESET} {p_name}")
    
    if not printers:
        print(f"{Colors.RED}No printers found. Exiting.{Colors.RESET}")
    else:
        try:
            choice = int(input(f"\n{Colors.YELLOW}Select a printer to monitor (number): {Colors.RESET}"))
            chosen_printer = printers[choice]
            
            print(f"\n--- Monitoring {Colors.GREEN}{chosen_printer}{Colors.RESET} --- (Press Ctrl+C to stop)")
            for event in watch_printer_queue(chosen_printer):
                print(f"{Colors.MAGENTA}[EVENT]{Colors.RESET} {event}")
        except (ValueError, IndexError):
            print(f"{Colors.RED}Invalid selection. Exiting.{Colors.RESET}")
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Monitoring stopped by user.{Colors.RESET}")
