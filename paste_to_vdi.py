#!/usr/bin/env python3

"""
paste_to_vdi.py

This script facilitates data transfer to a Virtual Desktop Infrastructure (VDI) environment
by simulating keyboard input and clipboard operations. It supports various modes including
text, spreadsheet, image, and code editor transfers.

The script uses xdotool to interact with windows in a Linux environment, allowing for
automated input into applications running within a VDI session.

Usage:
    python paste_to_vdi.py [-s|-t|-i|-e] [-w <window_title>] [-c] [-d] [<path_to_file>]

Options:
    -s              Spreadsheet mode
    -t              Text editor mode
    -i              Image transfer mode
    -e              Code editor mode (Visual Studio Code)
    -w <window_title> Specify window title (optional)
    -c              Use clipboard contents as input (no file needed)
    -d              Enable debug logging

Dependencies:
    - xdotool
    - pyautogui
    - pyperclip
    - python-dotenv

Environment variables (configured in .env file):
    WINDOW_TITLE
    DELAY_BETWEEN_KEYS
    DELAY_BETWEEN_COMMANDS
    DELAY_BETWEEN_APPLICATIONS
    NOTEPAD_LOAD_TIME
    EXCEL_LOAD_TIME
    VSCODE_LOAD_TIME
    CHUNK_SIZE
    DELAY_BETWEEN_CHUNKS

Author: Jerry Keen
Date: July 17, 2024
Version: 1.0
"""

import sys
import os
import argparse
import tempfile
import time
import pyautogui
import pyperclip
from base64 import b64encode
from dotenv import load_dotenv
import shlex
import subprocess
import re
import logging

# Load environment variables from .env file
load_dotenv()

# Configuration from .env
WINDOW_TITLE = os.getenv('WINDOW_TITLE', 'vdi_window_title - Brave')
DELAY_BETWEEN_KEYS = float(os.getenv('DELAY_BETWEEN_KEYS', 0.05))
DELAY_BETWEEN_COMMANDS = float(os.getenv('DELAY_BETWEEN_COMMANDS', 0.2))
DELAY_BETWEEN_APPLICATIONS = float(os.getenv('DELAY_BETWEEN_APPLICATIONS', 1))
NOTEPAD_LOAD_TIME = float(os.getenv('NOTEPAD_LOAD_TIME', 2))
EXCEL_LOAD_TIME = float(os.getenv('EXCEL_LOAD_TIME', 5))
VSCODE_LOAD_TIME = float(os.getenv('VSCODE_LOAD_TIME', 3))
CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 5))
DELAY_BETWEEN_CHUNKS = float(os.getenv('DELAY_BETWEEN_CHUNKS', 0.5))

# Enable debug logging (default: false)
DEBUG = False

# Global variable to store the target window ID
WINDOW_ID = ""

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def debug_log(message):
    """
    Log debug messages if debug mode is enabled.

    Args:
        message (str): The message to log.

    Returns:
        None

    This function logs debug messages using the logger's debug method.
    It should only be called when detailed logging is necessary for troubleshooting.
    """
    logger.debug(message)

def usage():
    """
    Display usage information for the script.

    Args:
        None

    Returns:
        None

    This function prints detailed usage instructions for the script,
    including available options and example commands. After displaying
    the information, it exits the script with a status code of 1.
    """
    print("""
Usage: python paste_to_vdi.py [-s|-t|-i|-e] [-w <window_title>] [-c] [-d] [<path_to_file>]

Options:
  -s              Spreadsheet mode
  -t              Text editor mode
  -i              Image transfer mode
  -e              Code editor mode (Visual Studio Code)
  -w <window_title> Specify window title (optional)
  -c              Use clipboard contents as input (no file needed)
  -d              Enable debug logging
  -h              Display this help message

Examples:
1. Text Mode with File Input:
   python paste_to_vdi.py -t -w "vdi_window_title - Brave" /path/to/textfile.txt

2. Text Mode with Clipboard Input:
   python paste_to_vdi.py -t -w "vdi_window_title - Brave" -c

3. Spreadsheet Mode with File Input:
   python paste_to_vdi.py -s -w "vdi_window_title - Brave" /path/to/spreadsheetfile.csv

4. Spreadsheet Mode with Clipboard Input:
   python paste_to_vdi.py -s -w "vdi_window_title - Brave" -c

5. Image Mode with File Input:
   python paste_to_vdi.py -i -w "vdi_window_title - Brave" /path/to/imagefile.png

6. Image Mode with Clipboard Input:
   python paste_to_vdi.py -i -w "vdi_window_title - Brave" -c

7. Code Mode with File Input:
   python paste_to_vdi.py -e -w "vdi_window_title - Brave" /path/to/codefile.py

8. Code Mode with Clipboard Input:
   python paste_to_vdi.py -e -w "vdi_window_title - Brave" -c
""")
    exit(1)

def get_clipboard_content():
    """
    Retrieve content from the clipboard.

    Args:
        None

    Returns:
        str: The content of the clipboard.

    This function uses pyperclip to get the current contents of the system clipboard.
    It logs the action for debugging purposes.
    """
    debug_log(f"Getting clipboard content")
    return pyperclip.paste()

def set_clipboard_content(content):
    """
    Set content to the clipboard.

    Args:
        content (str): The content to be set in the clipboard.

    Returns:
        None

    This function uses pyperclip to set the provided content to the system clipboard.
    It logs the action for debugging purposes.
    """
    debug_log(f"Setting clipboard content")
    pyperclip.copy(content)

def convert_to_xdotool_key(char):
    """
    Convert a character to its corresponding xdotool key.

    Args:
        char (str): A single character to be converted.

    Returns:
        str: The xdotool key representation of the input character.

    This function maps special characters to their xdotool key equivalents.
    If the character is not in the mapping, it returns the character as-is.
    """
    mapping = {
        ' ': 'space', '!': 'exclam', '"': 'quotedbl', '#': 'numbersign', '$': 'dollar',
        '%': 'percent', '&': 'ampersand', "'": 'apostrophe', '(': 'parenleft', ')': 'parenright',
        '*': 'asterisk', '+': 'plus', ',': 'comma', '-': 'minus', '.': 'period',
        '/': 'slash', '\\': 'backslash', ':': 'colon', ';': 'semicolon', '<': 'less',
        '=': 'equal', '>': 'greater', '?': 'question', '@': 'at', '[': 'bracketleft',
        ']': 'bracketright', '^': 'asciicircum', '_': 'underscore', '`': 'grave',
        '{': 'braceleft', '|': 'bar', '}': 'braceright', '~': 'asciitilde',
        '\n': 'Return'
    }
    return mapping.get(char, char)

def generate_xdotool_command(window_id, action, value):
    """
    Generate an xdotool command based on the action and value.

    Args:
        window_id (str): The ID of the target window.
        action (str): The action to perform ('type' or 'key').
        value (str): The value to be typed or the key to be pressed.

    Returns:
        list: A list of strings representing the xdotool command.

    Raises:
        ValueError: If an unsupported action is provided.

    This function creates the appropriate xdotool command based on the given action and value.
    """
    if action == "type":
        return ['xdotool', 'type', '--window', window_id, value]
    elif action == "key":
        return ['xdotool', 'key', '--window', window_id, value]
    else:
        raise ValueError(f"Unsupported action: {action}")

def send_command_to_window(window_id, action, value):
    """
    Send a command to the target window using xdotool, honoring CHUNK_SIZE.

    Args:
        window_id (str): The ID of the target window.
        action (str): The action to perform ('type' or 'key').
        value (str): The value to be typed or the key to be pressed.

    Returns:
        bool: True if the command was executed successfully, False otherwise.

    This function sends commands to the target window using xdotool. For 'type' actions,
    it breaks the input into chunks to prevent buffer overload. It logs all actions
    and any errors that occur during execution.
    """
    activate_window(window_id)
    try:
        if action == "type":
            for i in range(0, len(value), CHUNK_SIZE):
                chunk = value[i:i+CHUNK_SIZE]
                command = generate_xdotool_command(window_id, action, chunk)
                command_str = ' '.join(command)
                debug_log(f"Sending chunk: {chunk}")
                debug_log(f"xdotool command: {command_str}")
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                debug_log(f"Executed command: {command_str}")
                debug_log(f"Command output: {result.stdout}")
                time.sleep(DELAY_BETWEEN_COMMANDS)  # Adding delay to prevent buffer overload
        else:
            command = generate_xdotool_command(window_id, action, value)
            command_str = ' '.join(command)
            debug_log(f"xdotool command: {command_str}")
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            debug_log(f"Executed command: {command_str}")
            debug_log(f"Command output: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command for window ID {window_id}")
        debug_log(f"Command failed: {e}")
        debug_log(f"Error output: {e.stderr}")
        return False

def activate_window(window_id):
    """
    Activate and focus the target window.

    Args:
        window_id (str): The ID of the window to activate.

    Returns:
        None

    This function uses xdotool to activate and raise the specified window,
    bringing it to the foreground. It logs any errors that occur during
    the process.
    """
    try:
        subprocess.run(['xdotool', 'windowactivate', '--sync', window_id], check=True)
        subprocess.run(['xdotool', 'windowraise', window_id], check=True)
        time.sleep(DELAY_BETWEEN_COMMANDS)
        debug_log(f"Activated and raised window {window_id}")
    except subprocess.CalledProcessError as e:
        print(f"Error activating window {window_id}: {e}")
        debug_log(f"Error activating window: {e}")

def find_window_id(title):
    """
    Find the window ID based on the window title.

    Args:
        title (str): The title of the window to find.

    Returns:
        str or None: The ID of the found window, or None if not found.

    This function uses xdotool to search for a window with the given title.
    It returns the ID of the most recently active window matching the title.
    If no window is found, it returns None and logs an error message.
    """
    try:
        result = subprocess.run(['xdotool', 'search', '--name', title], capture_output=True, text=True, check=True)
        window_ids = result.stdout.strip().split('\n')
        return window_ids[-1] if window_ids else None  # Return the last (most recently active) window ID
    except subprocess.CalledProcessError:
        print(f"Error: Failed to find window with title '{title}'.")
        return None


def send_text_to_window(window_id, text):
    """
    Send text to the target window, handling special characters and preserving formatting.

    Args:
        window_id (str): The ID of the target window.
        text (str): The text to be sent to the window.

    Returns:
        None

    This function sends text to the target window character by character,
    converting special characters to their xdotool equivalents. It preserves
    formatting by sending appropriate key commands for newlines and other
    special characters. It also reports progress as a percentage of characters sent.
    """
    total_length = len(text)
    chars_sent = 0
    for char in text:
        xdotool_key = convert_to_xdotool_key(char)
        send_command_to_window(window_id, "key", xdotool_key)
        time.sleep(DELAY_BETWEEN_KEYS)
        chars_sent += 1
        progress = (chars_sent / total_length) * 100
        print(f"PROGRESS:{progress:.2f}", flush=True)
        debug_log(f"Sent character: {char}, Progress: {progress:.2f}%")


def send_line_spreadsheet(line, current_line, total_lines):
    """
    Send a line of text to the spreadsheet application.

    Args:
        line (str): A line of text to be sent to the spreadsheet.
        current_line (int): The current line number being processed.
        total_lines (int): The total number of lines to be processed.

    Returns:
        None

    This function sends a line of text to a spreadsheet application,
    separating values by tabs and moving to the next row after each line.
    It ignores empty lines and lines starting with '#'.
    """
    debug_log(f"Sending line in spreadsheet mode: {line}")
    parts = line.split('\t')
    for i, part in enumerate(parts):
        send_command_to_window(WINDOW_ID, "type", part)
        if i < len(parts) - 1:
            send_command_to_window(WINDOW_ID, "key", "Tab")
        time.sleep(DELAY_BETWEEN_COMMANDS)
    send_command_to_window(WINDOW_ID, "key", "Return")
    time.sleep(DELAY_BETWEEN_COMMANDS)
    progress = (current_line / total_lines) * 100
    print(f"PROGRESS:{progress:.2f}", flush=True)

def open_notepad():
    """
    Open a new instance of Notepad.

    Args:
        None

    Returns:
        None

    This function simulates keyboard input to open a new instance of Notepad
    in the VDI environment. It uses the Windows Start menu to search for and
    launch Notepad.
    """
    debug_log("Opening a new instance of Notepad")
    send_command_to_window(WINDOW_ID, "key", "ctrl+Escape")
    time.sleep(DELAY_BETWEEN_APPLICATIONS)
    send_command_to_window(WINDOW_ID, "type", "notepad")
    time.sleep(DELAY_BETWEEN_APPLICATIONS)
    send_command_to_window(WINDOW_ID, "key", "Return")
    time.sleep(NOTEPAD_LOAD_TIME)

def open_excel():
    """
    Open a new instance of Excel.

    Args:
        None

    Returns:
        None

    This function simulates keyboard input to open a new instance of Excel
    in the VDI environment. It uses the Windows Start menu to search for and
    launch Excel.
    """
    debug_log("Opening a new instance of Excel")
    send_command_to_window(WINDOW_ID, "key", "ctrl+Escape")
    time.sleep(DELAY_BETWEEN_APPLICATIONS)
    send_command_to_window(WINDOW_ID, "type", "excel")
    time.sleep(DELAY_BETWEEN_APPLICATIONS)
    send_command_to_window(WINDOW_ID, "key", "Return")
    time.sleep(EXCEL_LOAD_TIME)

def open_vscode():
    """
    Open a new instance of Visual Studio Code and prepare to paste content.

    Args:
        None

    Returns:
        None

    This function simulates keyboard input to open a new instance of Visual Studio Code
    in the VDI environment. It uses the Windows Start menu to search for and launch VSCode,
    then opens a new file to prepare for content pasting.
    """
    debug_log("Opening a new instance of Visual Studio Code")
    send_command_to_window(WINDOW_ID, "key", "ctrl+Escape")
    time.sleep(DELAY_BETWEEN_APPLICATIONS)
    send_command_to_window(WINDOW_ID, "type", "Visual studio code")
    time.sleep(DELAY_BETWEEN_APPLICATIONS)
    send_command_to_window(WINDOW_ID, "key", "Return")
    time.sleep(VSCODE_LOAD_TIME)
    send_command_to_window(WINDOW_ID, "key", "alt")
    send_command_to_window(WINDOW_ID, "key", "f")
    send_command_to_window(WINDOW_ID, "key", "return")

def send_image(image_data):
    """
    Send image data to the target window.

    Args:
        image_data (str): Base64 encoded image data.

    Returns:
        None

    This function sends the provided image data to the target window by opening
    Notepad and typing the encoded data. It uses a temporary file to store the
    data before sending it to the VDI environment.
    """
    debug_log("Sending image data to VDI and automating Notepad")
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(image_data.encode('utf-8'))
        temp_file_path = temp_file.name
    debug_log(f"Created temporary file: {temp_file_path}")
    activate_window(WINDOW_ID)
    open_notepad()
    time.sleep(DELAY_BETWEEN_APPLICATIONS)
    debug_log("Typing encoded image data from file")
    with open(temp_file_path, 'r') as temp_file:
        for line in temp_file:
            send_command_to_window(WINDOW_ID, "type", line)
            time.sleep(DELAY_BETWEEN_KEYS)
    os.remove(temp_file_path)
    debug_log("Removed temporary file")


def main():
    """
    Main function to handle command-line arguments and execute the appropriate actions.

    Args:
        None

    Returns:
        None

    This function parses command-line arguments, sets up the environment based on those
    arguments, and executes the appropriate data transfer mode (text, spreadsheet, image, or code).
    It also handles progress reporting for text and spreadsheet modes.
    """
    global WINDOW_ID

    parser = argparse.ArgumentParser(description="VDI Data Transfer Script")
    parser.add_argument('-s', action='store_true', help='Spreadsheet mode')
    parser.add_argument('-t', action='store_true', help='Text editor mode')
    parser.add_argument('-i', action='store_true', help='Image transfer mode')
    parser.add_argument('-e', action='store_true', help='Code editor mode (Visual Studio Code)')
    parser.add_argument('-w', type=str, help='Specify window title')
    parser.add_argument('-c', action='store_true', help='Use clipboard contents as input')
    parser.add_argument('-d', action='store_true', help='Enable debug logging')
    parser.add_argument('path_to_file', nargs='?', help='Path to file (optional)')
    args = parser.parse_args()

    if args.d:
        logger.setLevel(logging.DEBUG)
        debug_log("Debug logging enabled")

    window_title = args.w if args.w else WINDOW_TITLE
    USE_CLIPBOARD = args.c

    # Determine input source (clipboard or file)
    if USE_CLIPBOARD:
        debug_log("Using clipboard as input")
        clipboard_content = get_clipboard_content()
    elif args.path_to_file:
        file_path = args.path_to_file
        debug_log(f"Using file as input: {file_path}")
    else:
        logger.error("No input source specified (clipboard or file)")
        sys.exit(1)

    # Find and activate the target window
    WINDOW_ID = find_window_id(window_title)
    if not WINDOW_ID:
        logger.error(f"Could not find window with title '{window_title}'.")
        sys.exit(1)

    debug_log(f"Target Window ID: {WINDOW_ID}")
    logger.info(f"Starting data transfer to window: {window_title}")

    # Execute the appropriate mode
    if args.s:
        debug_log("Entering spreadsheet mode")
        activate_window(WINDOW_ID)
        open_excel()
        total_lines = 0
        current_line = 0
        if USE_CLIPBOARD:
            lines = clipboard_content.splitlines()
            total_lines = len(lines)
            for line in lines:
                if line.strip() and not line.strip().startswith('#'):
                    current_line += 1
                    send_line_spreadsheet(line, current_line, total_lines)
        else:
            with open(file_path, 'r') as f:
                total_lines = sum(1 for line in f if line.strip() and not line.strip().startswith('#'))
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip() and not line.strip().startswith('#'):
                        current_line += 1
                        send_line_spreadsheet(line, current_line, total_lines)
    elif args.t:
        debug_log("Entering text mode")
        activate_window(WINDOW_ID)
        open_notepad()
        if USE_CLIPBOARD:
            send_text_to_window(WINDOW_ID, clipboard_content)
        else:
            with open(file_path, 'r') as f:
                content = f.read()
            send_text_to_window(WINDOW_ID, content)

    elif args.i:
        debug_log("Entering image mode")
        # Image mode implementation (no progress reporting for now)
    elif args.i:
        if USE_CLIPBOARD:
            send_image(clipboard_content)
        else:
            with open(file_path, 'rb') as f:
                encoded_image = b64encode(f.read()).decode('utf-8')
            image_data = f"START_IMAGE\n{encoded_image}\nEND_IMAGE"
            send_image(image_data)
    elif args.e:
            debug_log("Entering code mode")
            activate_window(WINDOW_ID)
            open_vscode()
            if USE_CLIPBOARD:
                send_text_to_window(WINDOW_ID, clipboard_content)
            else:
                with open(file_path, 'r') as f:
                    content = f.read()
                send_text_to_window(WINDOW_ID, content)
    else:
        print("Error: Invalid mode selected.")
        usage()

    print("PROGRESS:100.00", flush=True)  # Indicate completion
    logger.info("Data transfer completed successfully")

if __name__ == "__main__":
    main()
