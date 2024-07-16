import sys
import os
import argparse
import tempfile
import time
import pyautogui
import pyperclip
from base64 import b64encode

# Enable debug logging (default: false)
DEBUG = False

# Global variable to store the target window title
WINDOW_TITLE = ""
WINDOW_ID = ""

def debug_log(message):
    if DEBUG:
        print(f"[DEBUG] {message}")

def usage():
    print("""
Usage: python paste_to_vdi.py [-s|-t|-i] [-w <window_title>] [-c] [-d] [<path_to_file>]

Options:
  -s              Spreadsheet mode
  -t              Text editor mode
  -i              Image transfer mode
  -w <window_title> Specify window title (optional)
  -c              Use clipboard contents as input (no file needed)
  -d              Enable debug logging
  -h              Display this help message

Examples:

1. Text Mode with File Input:
   Send the contents of a text file to the specified window.
   Command:
   /usr/bin/python3 /path/to/paste_to_vdi.py -t -w "NextGen VDI - Brave" /path/to/textfile.txt

2. Text Mode with Clipboard Input:
   Send the contents of the clipboard to the specified window.
   Command:
   /usr/bin/python3 /path/to/paste_to_vdi.py -t -w "NextGen VDI - Brave" -c

3. Spreadsheet Mode with File Input:
   Send the contents of a CSV file to Excel in the specified window.
   Command:
   /usr/bin/python3 /path/to/paste_to_vdi.py -s -w "NextGen VDI - Brave" /path/to/spreadsheetfile.csv

4. Spreadsheet Mode with Clipboard Input:
   Send the contents of the clipboard (tab-delimited) to Excel in the specified window.
   Command:
   /usr/bin/python3 /path/to/paste_to_vdi.py -s -w "NextGen VDI - Brave" -c

5. Image Mode with File Input:
   Send the contents of an image file (encoded) to Notepad in the specified window.
   Command:
   /usr/bin/python3 /path/to/paste_to_vdi.py -i -w "NextGen VDI - Brave" /path/to/imagefile.png

6. Image Mode with Clipboard Input:
   Send the contents of the clipboard (encoded image) to Notepad in the specified window.
   Command:
   /usr/bin/python3 /path/to/paste_to_vdi.py -i -w "NextGen VDI - Brave" -c
""")
    exit(1)


def get_clipboard_content():
    debug_log(f"Getting clipboard content")
    return pyperclip.paste()

def set_clipboard_content(content):
    debug_log(f"Setting clipboard content")
    pyperclip.copy(content)

def send_line_spreadsheet(line):
    debug_log(f"Sending line in spreadsheet mode: {line}")
    parts = line.split('\t')
    for i, part in enumerate(parts):
        send_text_to_window(part)
        if i < len(parts) - 1:
            send_key_to_window('Tab')
            time.sleep(0.2)
    send_key_to_window('Return')
    time.sleep(0.5)

def send_text(text):
    debug_log("Sending text in text editor mode")
    debug_log(f"Text length: {len(text)} characters")
    activate_window(WINDOW_ID)
    open_notepad()
    for char in text:
        send_text_to_window(char)
        time.sleep(0.05 if char != '\n' else 0.1)
    copy_notepad_content()
    close_notepad()
    debug_log("Text operation completed")

def send_image(image_data):
    debug_log("Sending image data to VDI and automating Notepad")
    with tempfile.NamedTemporaryFile(delete=False) as temp_file:
        temp_file.write(image_data.encode('utf-8'))
        temp_file_path = temp_file.name
    debug_log(f"Created temporary file: {temp_file_path}")
    activate_window(WINDOW_ID)
    open_notepad()
    time.sleep(1)
    debug_log("Typing encoded image data from file")
    with open(temp_file_path, 'r') as temp_file:
        for line in temp_file:
            send_text_to_window(line)
            time.sleep(0.05)
    copy_notepad_content()
    close_notepad()
    os.remove(temp_file_path)
    debug_log("Removed temporary file")

def send_text_to_window(text):
    command = f'xdotool type --window {WINDOW_ID} "{text}"'
    debug_log(f"Running command: {command}")
    result = os.system(command)
    debug_log(f"Command result: {result}")
    if result != 0:
        print(f"Error sending text '{text}' to window ID {WINDOW_ID}")

def send_key_to_window(key):
    command = f'xdotool key --window {WINDOW_ID} {key}'
    debug_log(f"Running command: {command}")
    result = os.system(command)
    debug_log(f"Command result: {result}")
    if result != 0:
        print(f"Error sending key '{key}' to window ID {WINDOW_ID}")

def activate_window(window_id):
    command = f'xdotool windowactivate {window_id} && xdotool windowfocus {window_id}'
    debug_log(f"Activating window with command: {command}")
    result = os.system(command)
    debug_log(f"Activation result: {result}")
    if result != 0:
        print(f"Error activating window ID {window_id}")

def find_window_id(title):
    result = os.popen(f'xdotool search --name "{title}"').read().strip()
    return result.split('\n')[0] if result else None

def open_notepad():
    debug_log("Opening a new instance of Notepad")
    send_key_to_window('ctrl+Escape')
    time.sleep(1)
    send_text_to_window('notepad')
    time.sleep(1)
    send_key_to_window('Return')
    time.sleep(2)

def open_excel():
    debug_log("Opening a new instance of Excel")
    send_key_to_window('ctrl+Escape')
    time.sleep(1)
    send_text_to_window('excel')
    time.sleep(1)
    send_key_to_window('Return')
    time.sleep(5)  # Allow extra time for Excel to open

def copy_notepad_content():
    debug_log("Copying Notepad content to the clipboard")
    send_key_to_window('ctrl+a')
    time.sleep(1)
    send_key_to_window('ctrl+c')
    time.sleep(1)

def close_notepad():
    debug_log("Closing Notepad")
    send_key_to_window('alt+F')
    time.sleep(0.2)
    send_key_to_window("e")
    time.sleep(0.2)
    send_key_to_window('Tab')
    time.sleep(0.2)
    send_key_to_window('space')
    time.sleep(0.2)

def main():
    global DEBUG, WINDOW_TITLE, WINDOW_ID

    parser = argparse.ArgumentParser(description="VDI Data Transfer Script")
    parser.add_argument('-s', action='store_true', help='Spreadsheet mode')
    parser.add_argument('-t', action='store_true', help='Text editor mode')
    parser.add_argument('-i', action='store_true', help='Image transfer mode')
    parser.add_argument('-w', type=str, help='Specify window title')
    parser.add_argument('-c', action='store_true', help='Use clipboard contents as input')
    parser.add_argument('-d', action='store_true', help='Enable debug logging')
    parser.add_argument('path_to_file', nargs='?', help='Path to file (optional)')
    args = parser.parse_args()

    DEBUG = args.d
    WINDOW_TITLE = args.w
    USE_CLIPBOARD = args.c

    if not any([args.s, args.t, args.i]):
        if USE_CLIPBOARD:
            args.t = True
        else:
            print("Error: No mode selected.")
            usage()

    if not USE_CLIPBOARD and not args.path_to_file:
        print("Error: File path not provided.")
        usage()

    clipboard_content = None
    if USE_CLIPBOARD:
        debug_log("Using clipboard as input")
        clipboard_content = get_clipboard_content()
        if not clipboard_content:
            print("Error: Clipboard is empty.")
            exit(1)
    else:
        file_path = args.path_to_file
        debug_log(f"Using file as input: {file_path}")
        if not os.path.isfile(file_path):
            print(f"Error: File not found: {file_path}")
            exit(1)

    if not WINDOW_TITLE:
        WINDOW_TITLE = "NextGen VDI - Brave"

    WINDOW_ID = find_window_id(WINDOW_TITLE)
    if not WINDOW_ID:
        print(f"Error: Could not find window with title '{WINDOW_TITLE}'.")
        exit(1)

    debug_log(f"Target Window ID: {WINDOW_ID}")
    print(f"Target Window Title: {WINDOW_TITLE}")
    print(f"Target Window ID: {WINDOW_ID}")
    print("The script will now attempt to send data to the window.")
    print("Starting in 5 seconds...")
    time.sleep(5)

    mode = None
    if args.s:
        mode = "spreadsheet"
    elif args.t:
        mode = "text"
    elif args.i:
        mode = "image"

    debug_log(f"Processing in {mode} mode")
    print(f"Processing in {mode} mode...")

    if mode == "spreadsheet":
        activate_window(WINDOW_ID)
        open_excel()
        if USE_CLIPBOARD:
            for line in clipboard_content.splitlines():
                if line.strip() and not line.strip().startswith('#'):
                    send_line_spreadsheet(line)
        else:
            with open(file_path, 'r') as f:
                for line in f:
                    if line.strip() and not line.strip().startswith('#'):
                        send_line_spreadsheet(line)
    elif mode == "text":
        if USE_CLIPBOARD:
            send_text(clipboard_content)
        else:
            with open(file_path, 'r') as f:
                content = f.read()
            send_text(content)
    elif mode == "image":
        if USE_CLIPBOARD:
            send_image(clipboard_content)
        else:
            with open(file_path, 'rb') as f:
                encoded_image = b64encode(f.read()).decode('utf-8')
            image_data = f"START_IMAGE\n{encoded_image}\nEND_IMAGE"
            send_image(image_data)
    else:
        print("Error: Invalid mode selected.")
        usage()

    debug_log("Finished sending data to the window")
    print("Finished sending data to the window")

if __name__ == "__main__":
    main()
