"""
The Monitor Module: The Eyes and Ears

This script is the agent's connection to the physical world. It uses the
ctypes library to call Windows API functions directly, bypassing limitations
in pywin32 to achieve an efficient, event-driven monitoring of the printer queue.
"""

import ctypes
from ctypes import wintypes

import pywintypes
import win32print

from .const import Colors
from .utils import get_available_printers, get_job_status_string

# --- ctypes Setup for Windows API Calls ---
# Load necessary libraries
winspool = ctypes.WinDLL("winspool.drv", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32.dll", use_last_error=True)

# --- Win32 Constants ---
PRINTER_CHANGE_ADD_JOB = 0x00000100
PRINTER_CHANGE_SET_JOB = 0x00000200
PRINTER_CHANGE_DELETE_JOB = 0x00000400
# Note: INVALID_HANDLE_VALUE is the integer value, not a ctypes object.
INVALID_HANDLE_VALUE = -1
INFINITE = 0xFFFFFFFF

# --- ctypes Function Prototypes ---
# Define the argument types and return types for the Win32 functions we need.
winspool.OpenPrinterW.argtypes = [wintypes.LPWSTR, wintypes.LPHANDLE, wintypes.LPVOID]
winspool.OpenPrinterW.restype = wintypes.BOOL

winspool.ClosePrinter.argtypes = [wintypes.HANDLE]
winspool.ClosePrinter.restype = wintypes.BOOL

winspool.FindFirstPrinterChangeNotification.argtypes = [
    wintypes.HANDLE,
    wintypes.DWORD,
    wintypes.DWORD,
    wintypes.LPVOID,
]
# The return type is a handle, which ctypes treats as an integer.
winspool.FindFirstPrinterChangeNotification.restype = wintypes.HANDLE

winspool.FindNextPrinterChangeNotification.argtypes = [
    wintypes.HANDLE,
    ctypes.POINTER(wintypes.DWORD),
    wintypes.LPVOID,
    wintypes.LPVOID,
]
winspool.FindNextPrinterChangeNotification.restype = wintypes.BOOL

winspool.FindClosePrinterChangeNotification.argtypes = [wintypes.HANDLE]
winspool.FindClosePrinterChangeNotification.restype = wintypes.BOOL

kernel32.WaitForSingleObject.argtypes = [wintypes.HANDLE, wintypes.DWORD]
kernel32.WaitForSingleObject.restype = wintypes.DWORD


def watch_printer_queue(printer_name: str):
    """Monitors a printer queue using a ctypes bridge to the Win32 API."""
    change_handle = None
    printer_handle = None
    try:
        # --- Open Printer Handle via ctypes ---
        printer_handle = wintypes.HANDLE()
        if not winspool.OpenPrinterW(printer_name, ctypes.byref(printer_handle), None):
            raise ctypes.WinError(ctypes.get_last_error())
        print(
            f"{Colors.GREEN}Successfully opened printer {printer_name}.{Colors.RESET}"
        )

        # --- Event-Driven Subscription via ctypes ---
        flags = (
            PRINTER_CHANGE_ADD_JOB | PRINTER_CHANGE_SET_JOB | PRINTER_CHANGE_DELETE_JOB
        )
        change_handle = winspool.FindFirstPrinterChangeNotification(
            printer_handle, flags, 0, None
        )

        if change_handle == INVALID_HANDLE_VALUE:
            raise ctypes.WinError(ctypes.get_last_error())

        print("Subscribed to printer change notifications. Waiting for events...")

        # --- Initial State Snapshot ---
        initial_jobs_info = win32print.EnumJobs(printer_handle.value, 0, -1, 2)
        last_jobs = {job["JobId"]: job for job in initial_jobs_info}
        print(f"Found {len(last_jobs)} existing jobs in the queue.")

        # --- Main Monitoring Loop ---
        while True:
            kernel32.WaitForSingleObject(change_handle, INFINITE)

            pdw_change = wintypes.DWORD()
            winspool.FindNextPrinterChangeNotification(
                change_handle, ctypes.byref(pdw_change), None, None
            )
            # print(
            #     f"{Colors.CYAN}Change detected on '{printer_name}'. Checking for jobs...{Colors.RESET}"
            # )

            current_jobs_info = win32print.EnumJobs(printer_handle.value, 0, -1, 2)
            current_jobs = {job["JobId"]: job for job in current_jobs_info}

            for job_id, job in current_jobs.items():
                if job_id not in last_jobs:
                    yield {"event": "new_job", "job_info": job}
                elif job["Status"] != last_jobs.get(job_id, {}).get("Status"):
                    statuses_to_report = {
                        win32print.JOB_STATUS_PAUSED,
                        win32print.JOB_STATUS_ERROR,
                        win32print.JOB_STATUS_OFFLINE,
                        win32print.JOB_STATUS_PAPEROUT,
                        win32print.JOB_STATUS_USER_INTERVENTION,
                        win32print.JOB_STATUS_BLOCKED_DEVQ,
                        win32print.JOB_STATUS_SPOOLING,
                        win32print.JOB_STATUS_PRINTED,
                    }
                    if any(job["Status"] & status for status in statuses_to_report):
                        yield {"event": "status_change", "job_info": job}

            for job_id in list(last_jobs.keys()):
                if job_id not in current_jobs:
                    yield {
                        "event": "job_deleted",
                        "job_info": last_jobs[job_id],
                    }

            last_jobs = current_jobs

    except Exception as e:
        yield f"{Colors.RED}An error occurred in the monitor thread: {e}{Colors.RESET}"

    finally:
        # --- Graceful Shutdown ---
        print(f"Shutting down monitoring for {printer_name}.")
        if change_handle and change_handle != INVALID_HANDLE_VALUE:
            winspool.FindClosePrinterChangeNotification(change_handle)
        if printer_handle and printer_handle.value:
            winspool.ClosePrinter(printer_handle)


if __name__ == "__main__":
    print(f"{Colors.BLUE}Available printers:{Colors.RESET}")
    printers = get_available_printers()
    for i, p_name in enumerate(printers):
        print(f"  {Colors.CYAN}[{i}]{Colors.RESET} {p_name}")

    if not printers:
        print(f"{Colors.RED}No printers found. Exiting.{Colors.RESET}")
    else:
        try:
            choice = int(
                input(
                    f"\n{Colors.YELLOW}Select a printer to monitor (number): {Colors.RESET}"
                )
            )
            chosen_printer = printers[choice]

            print(
                f"\n--- Monitoring {Colors.GREEN}{chosen_printer}{Colors.RESET} --- (Press Ctrl+C to stop)"
            )
            for event in watch_printer_queue(chosen_printer):
                print(f"{Colors.MAGENTA}[EVENT]{Colors.RESET} {event}")
        except (ValueError, IndexError):
            print(f"{Colors.RED}Invalid selection. Exiting.{Colors.RESET}")
        except KeyboardInterrupt:
            print(f"\n{Colors.YELLOW}Monitoring stopped by user.{Colors.RESET}")
