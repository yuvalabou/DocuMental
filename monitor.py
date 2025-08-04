"""
The Monitor Module

This script is the core of the project. It's a Python script that only does one
thing: it watches the printer queue and detects changes. It doesn't talk to the
LLM or send notifications. It simply logs or prints out what's happening.
"""

import time
import win32print

def watch_printer_queue(printer_name="Microsoft Print to PDF"):
    """
    Monitors a specified printer queue for job status changes.

    This function runs in an infinite loop to continuously check for new jobs,
    completed jobs, or changes in job statuses (e.g., from spooling to error).

    Args:
        printer_name (str): The name of the printer to monitor.
                            Defaults to "Microsoft Print to PDF".
    """
    print(f"Starting to monitor printer: {printer_name}")
    last_jobs = {}

    # --- To be implemented ---
    # 1. Initialize a connection to the printer using pywin32.
    #    - Use win32print.OpenPrinter(printer_name)

    # 2. Run an infinite loop.
    while True:
        # 3. Inside the loop, get the current state of all jobs in the queue.
        #    - Use win32print.EnumJobs to get job details.

        # 4. Compare the current state to the last known state.
        #    - Check for new jobs.
        #    - Check for status changes in existing jobs.
        #    - Check for completed/removed jobs.

        # 5. If there are changes, print a clean, structured message.
        #    - Example: "Job ID 123: New job, 'Resume.pdf'"
        #    - Example: "Job ID 124: Status change to 'ERROR' - Paper Jam"

        # 6. Sleep for a few seconds before the next check.
        print("Checking for print jobs...") # Placeholder
        time.sleep(5)

if __name__ == '__main__':
    # This allows you to run the monitor independently for testing.
    # You can find your printer name in Windows Settings > Bluetooth & devices > Printers & scanners.
    my_printer_name = "Microsoft Print to PDF"  # <--- CHANGE THIS TO YOUR PRINTER'S NAME
    watch_printer_queue(my_printer_name)
