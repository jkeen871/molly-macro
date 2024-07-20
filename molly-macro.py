#!/usr/bin/env python3

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
import json
import logging

# Load environment variables from .env file
load_dotenv()

# Set up logging
logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s - %(message)s',
                    handlers=[logging.StreamHandler(sys.stdout)])
logger = logging.getLogger(__name__)

# Global configuration variables
WINDOW_ID = ""
config = {}
app_config = {}
DEBUG = False
USE_CLIPBOARD = False

def debug_log(message):
    """
    Log debug messages if debug mode is enabled.

    Args:
        message (str): The message to log.
    """
    if DEBUG:
        logger.debug(message)

def read_config(config_path):
    """
    Read and parse the JSON configuration file.

    Args:
        config_path (str): Path to the JSON configuration file.

    Returns:
        dict: Parsed configuration data.

    Raises:
        SystemExit: If the configuration file cannot be read or parsed.
    """
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)
        debug_log(f"Configuration loaded from {config_path}")
        return config
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse configuration file: {e}")
        sys.exit(1)
    except IOError as e:
        logger.error(f"Failed to read configuration file: {e}")
        sys.exit(1)

def load_config(config_path, config_name):
    """
    Load configuration from a JSON file and update global variables.

    Args:
        config_path (str): Path to the configuration file.
        config_name (str): Name of the configuration to load.

    Raises:
        SystemExit: If configuration loading fails.
    """
    global config, app_config
    try:
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)

        app_config = config['applications'].get(config_name, {})

        # Load settings from config, use .env values as defaults
        for key in ["WINDOW_TITLE", "DELAY_BETWEEN_KEYS", "DELAY_BETWEEN_COMMANDS",
                    "DELAY_BETWEEN_APPLICATIONS", "APP_LOAD_TIME", "CHUNK_SIZE", "DELAY_BETWEEN_CHUNKS"]:
            if key not in app_config:
                app_config[key] = os.getenv(key)

        # Convert numeric values to appropriate types
        for key in ["DELAY_BETWEEN_KEYS", "DELAY_BETWEEN_COMMANDS", "DELAY_BETWEEN_APPLICATIONS",
                    "APP_LOAD_TIME", "CHUNK_SIZE", "DELAY_BETWEEN_CHUNKS"]:
            if key in app_config:
                app_config[key] = float(app_config[key])

        logger.debug(f"Loaded configuration for {config_name}: {app_config}")
    except Exception as e:
        logger.error(f"Failed to load configuration: {e}")
        sys.exit(1)

def execute_steps(window_id, steps):
    """
    Execute a series of steps on a specified window.

    Args:
        window_id (str): The ID of the window to operate on.
        steps (list): A list of step dictionaries to execute.

    Returns:
        bool: True if all steps executed successfully, False otherwise.
    """
    debug_log(f"Executing steps for window ID: {window_id}")
    for step in steps:
        action = step['action']
        value = step.get('value', '')
        debug_log(f"Executing step: Action: {action}, Value: {value}")
        if action == 'launch_window':
            continue  # launch_window is handled separately
        if not send_command_to_window(window_id, action, value):
            logger.error(f"Failed to execute step: {step}")
            return False
    return True

def convert_to_xdotool_key(char):
    """
    Convert a character to its corresponding xdotool key.

    Args:
        char (str): The character to convert.

    Returns:
        str: The xdotool key representation of the character.
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
        window_id (str): The ID of the window to operate on.
        action (str): The action to perform.
        value (str): The value associated with the action.

    Returns:
        list: A list of command arguments for subprocess.

    Raises:
        ValueError: If an unsupported action is provided.
    """
    if action == "type":
        return ['xdotool', 'type', '--window', window_id, value]
    elif action == "key":
        return ['xdotool', 'key', '--window', window_id, value]
    elif action == "raise_window":
        return ['xdotool', 'windowraise', window_id]
    else:
        raise ValueError(f"Unsupported action: {action}")

def send_command_to_window(window_id, action, value=None):
    """
    Send a command to a specified window using xdotool.

    Args:
        window_id (str): The ID of the window to operate on.
        action (str): The action to perform.
        value (str, optional): The value associated with the action.

    Returns:
        bool: True if the command was sent successfully, False otherwise.
    """
    debug_log(f"Sending command to window {window_id}: Action: {action}, Value: {value}")
    try:
        if action == "type":
            for i in range(0, len(value), int(app_config["CHUNK_SIZE"])):
                chunk = value[i:i + int(app_config["CHUNK_SIZE"])]
                command = generate_xdotool_command(window_id, action, chunk)
                command_str = ' '.join(command)
                debug_log(f"Sending chunk: {chunk}")
                debug_log(f"xdotool command: {command_str}")
                if not activate_window(window_id):
                    logger.error("Failed to activate window before sending command")
                    return False
                result = subprocess.run(command, check=True, capture_output=True, text=True)
                debug_log(f"Executed command: {command_str}")
                debug_log(f"Command output: {result.stdout}")
                time.sleep(app_config["DELAY_BETWEEN_CHUNKS"])
        else:
            command = generate_xdotool_command(window_id, action, value)
            command_str = ' '.join(command)
            debug_log(f"xdotool command: {command_str}")
            if not activate_window(window_id):
                logger.error("Failed to activate window before sending command")
                return False
            result = subprocess.run(command, check=True, capture_output=True, text=True)
            debug_log(f"Executed command: {command_str}")
            debug_log(f"Command output: {result.stdout}")

        time.sleep(app_config["DELAY_BETWEEN_COMMANDS"])
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Error executing command for window ID {window_id}")
        logger.error(f"Command failed: {e}")
        logger.error(f"Error output: {e.stderr}")
        return False

def activate_window(window_id):
    """
    Activate, focus, and raise the target window.

    Args:
        window_id (str): The ID of the window to activate.

    Returns:
        bool: True if the window was successfully activated, False otherwise.
    """
    debug_log(f"Activating window {window_id}")
    try:
        # First, try to activate the window
        result = subprocess.run(['xdotool', 'windowactivate', '--sync', window_id],
                                check=False, capture_output=True, text=True)
        if result.returncode != 0:
            logger.warning(f"Failed to activate window: {result.stderr}")
            # If activation fails, try to map the window first
            subprocess.run(['xdotool', 'windowmap', window_id], check=False)
            time.sleep(0.5)  # Give it a moment to map
            result = subprocess.run(['xdotool', 'windowactivate', '--sync', window_id],
                                    check=False, capture_output=True, text=True)

        # After activation, try to focus and raise the window
        subprocess.run(['xdotool', 'windowfocus', window_id], check=False)
        subprocess.run(['xdotool', 'windowraise', window_id], check=False)

        logger.info(f"Attempted to activate, focus, and raise window {window_id}")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to activate window {window_id}: {e}")
        return False

def launch_application(command, config):
    """
    Launch an application and find its window ID.

    Args:
        command (str): The command to launch the application.
        config (dict): The configuration dictionary for the application.

    Returns:
        str: The window ID of the launched application, or None if not found.
    """
    debug_log(f"Launching application with command: {command}")
    try:
        # Use subprocess.Popen with preexec_fn to detach the process
        process = subprocess.Popen(shlex.split(command),
                                   start_new_session=True,
                                   stdout=subprocess.DEVNULL,
                                   stderr=subprocess.DEVNULL)
        debug_log(f"Application process started with PID: {process.pid}")

        # Wait for the application to load
        app_load_time = float(config.get("APP_LOAD_TIME", 5.0))
        debug_log(f"Waiting {app_load_time} seconds for application to load")
        time.sleep(app_load_time)

        # Attempt to find the window ID using the window_match pattern from the config
        window_match = config.get("window_match")
        if not window_match:
            logger.error("No window_match pattern specified in the configuration")
            return None

        for attempt in range(10):  # Retry up to 10 times
            debug_log(f"Attempt {attempt + 1} to find window ID")
            time.sleep(1)  # Wait a moment before retrying
            result = subprocess.run(['xdotool', 'search', '--onlyvisible', '--name', window_match],
                                    check=False, capture_output=True, text=True)
            window_ids = result.stdout.split()
            debug_log(f"Found {len(window_ids)} visible windows")
            for window_id in window_ids:
                title_result = subprocess.run(['xdotool', 'getwindowname', window_id],
                                              check=False, capture_output=True, text=True)
                window_title = title_result.stdout.strip()
                debug_log(f"Checking window: ID={window_id}, Title='{window_title}'")
                if window_match in window_title:
                    logger.info(f"Found window ID for '{window_title}': {window_id}")
                    return window_id

        logger.error("Failed to find window ID for the launched application")
        return None
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to launch application: {e}")
        return None

def get_clipboard_content():
    """
    Retrieve the current clipboard content.

    Returns:
        str: The content of the clipboard.
    """
    try:
        clipboard_content = pyperclip.paste()
        debug_log(f"Clipboard content (first 100 chars): {clipboard_content[:100]}")
        return clipboard_content
    except Exception as e:
        logger.error(f"Failed to get clipboard content: {e}")
        return ""

def send_text_to_window(window_id, text):
    """
    Send text to the target window, handling special characters and preserving formatting.

    Args:
        window_id (str): The ID of the window to send text to.
        text (str): The text to send.

    Returns:
        bool: True if the text was sent successfully, False otherwise.
    """
    debug_log(f"Starting to send text to window {window_id}")
    debug_log(f"Text length: {len(text)}")
    debug_log(f"First 100 characters of text: {text[:100]}")

    if not text:
        logger.error("No text to send")
        return False

    # Activate and focus the window
    if not activate_window(window_id):
        logger.error("Failed to activate window before sending text")
        return False

    # Ensure the window is focused
    subprocess.run(['xdotool', 'windowfocus', window_id], check=True)
    time.sleep(0.5)  # Short delay to ensure the window is ready

    # Check if the window is still active right before sending text
    active_window = subprocess.run(['xdotool', 'getactivewindow'],
                                   check=False, capture_output=True, text=True)
    if active_window.stdout.strip() != window_id:
        logger.warning(f"Window {window_id} is not the active window before sending text")
        # Attempt to reactivate the window
        if not activate_window(window_id):
            logger.error("Failed to reactivate window before sending text")
            return False

    total_length = len(text)
    chars_sent = 0

    try:
        for char in text:
            if char == '\n':
                xdotool_key = 'Return'
            else:
                xdotool_key = convert_to_xdotool_key(char)

            debug_log(f"Sending character: {char} (converted to: {xdotool_key})")
            success = send_command_to_window(window_id, "key", xdotool_key)
            if not success:
                logger.error(f"Failed to send character: {char}")
                return False
            time.sleep(app_config["DELAY_BETWEEN_KEYS"])
            chars_sent += 1
            if chars_sent % 100 == 0 or chars_sent == total_length:
                progress = (chars_sent / total_length) * 100
                print(f"PROGRESS:{progress:.2f}", flush=True)
                debug_log(f"Sent {chars_sent}/{total_length} characters. Progress: {progress:.2f}%")

        debug_log("Finished sending text to window")
        return True
    except Exception as e:
        logger.error(f"Error sending text: {e}")
        return False

def main():
    """
    Main function to handle command-line arguments and execute the appropriate actions.

    This function performs the following steps:
    1. Parse command-line arguments
    2. Set up logging based on debug flag
    3. Determine input source (clipboard or file)
    4. Load and validate configuration
    5. Identify or launch the target window
    6. Execute open steps
    7. Check if payload should be sent
    8. If payload is to be sent, transfer data based on the specified mode

    Returns:
        None
    """
    global WINDOW_ID
    global DEBUG
    global USE_CLIPBOARD

    parser = argparse.ArgumentParser(description="VDI Data Transfer Script")
    parser.add_argument('-s', action='store_true', help='Spreadsheet mode')
    parser.add_argument('-t', action='store_true', help='Text editor mode')
    parser.add_argument('-i', action='store_true', help='Image transfer mode')
    parser.add_argument('-e', action='store_true', help='Code editor mode (Visual Studio Code)')
    parser.add_argument('-w', type=str, help='Specify window ID')
    parser.add_argument('-c', action='store_true', help='Use clipboard contents as input')
    parser.add_argument('-d', action='store_true', help='Enable debug logging')
    parser.add_argument('--config', type=str, default='config.json', help='Path to JSON configuration file')
    parser.add_argument('--config_name', type=str, help='Name of the configuration to use')
    parser.add_argument('--local', action='store_true', help='Indicate that this is a local configuration')
    parser.add_argument('path_to_file', nargs='?', help='Path to file (optional)')
    args = parser.parse_args()

    # Set up debug logging if requested
    if args.d:
        logger.setLevel(logging.DEBUG)
        global DEBUG
        DEBUG = True
        debug_log("Debug logging enabled")

    USE_CLIPBOARD = args.c

    # Determine input source (clipboard or file)
    if USE_CLIPBOARD:
        debug_log("Using clipboard as input")
        clipboard_content = get_clipboard_content()
    elif args.path_to_file:
        file_path = args.path_to_file
        debug_log(f"Using file as input: {file_path}")
    else:
        clipboard_content = ""
        file_path = ""

    # Read configuration
    config = read_config(args.config)
    debug_log(f"Configuration loaded from {args.config}")

    if not args.config_name:
        logger.error("No configuration name specified")
        sys.exit(1)

    # Load specific configuration for the selected application
    load_config(args.config, args.config_name)

    if not app_config:
        logger.error("Application configuration not found")
        sys.exit(1)

    debug_log(f"Using configuration: {args.config_name}")

    # Handle window identification or launch
    if app_config["type"] == "local" and "launch_command" in app_config:
        debug_log(f"Launching application with command: {app_config['launch_command']}")
        WINDOW_ID = launch_application(app_config["launch_command"], app_config)
        if not WINDOW_ID:
            logger.error("Failed to find window ID for the launched application")
            sys.exit(1)
    elif args.w:
        WINDOW_ID = args.w
        debug_log(f"Using provided window ID: {WINDOW_ID}")
    else:
        logger.error("No window ID specified")
        sys.exit(1)

    debug_log(f"Target Window ID: {WINDOW_ID}")

    # Execute open steps
    debug_log("Executing open steps")
    if not execute_steps(WINDOW_ID, app_config["open_steps"]):
        logger.error("Failed to execute open steps")
        sys.exit(1)

    # Check if payload should be sent
    if app_config.get("no_payload", False):
        logger.info("No payload option set to true. Skipping content transfer.")
        print("PROGRESS:100.00", flush=True)  # Indicate completion
        logger.info("Operation completed successfully without sending payload")
        sys.exit(0)

    # Determine the mode based on the configuration
    mode = app_config.get("mode")
    if not mode:
        logger.error("No mode selected")
        sys.exit(6)  # Invalid mode selected

    debug_log(f"Operating in {mode} mode")

    # Execute mode-specific operations
    if mode == "spreadsheet":
        debug_log("Entering spreadsheet mode")
        if USE_CLIPBOARD:
            clipboard_content = get_clipboard_content()
            if clipboard_content:
                debug_log("Sending clipboard content to spreadsheet")
                send_text_to_window(WINDOW_ID, clipboard_content)
            else:
                logger.error("No clipboard content to send")
        else:
            with open(file_path, 'r') as file:
                file_content = file.read()
            debug_log("Sending file content to spreadsheet")
            send_text_to_window(WINDOW_ID, file_content)
    elif mode == "text":
        debug_log("Entering text mode")
        content = clipboard_content if USE_CLIPBOARD else open(file_path).read()
        send_text_to_window(WINDOW_ID, content)
    elif mode == "image":
        debug_log("Entering image mode")
        logger.warning("Image mode not implemented yet")
        # Image mode operations (to be implemented)
    elif mode == "code":
        debug_log("Entering code mode")
        content = clipboard_content if USE_CLIPBOARD else open(file_path).read()
        send_text_to_window(WINDOW_ID, content)
    else:
        logger.error(f"Error: Invalid mode selected: {mode}")
        sys.exit(6)  # Invalid mode selected

    print("PROGRESS:100.00", flush=True)  # Indicate completion
    logger.info("Data transfer completed successfully")

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        logger.exception("An unexpected error occurred")
        sys.exit(7)