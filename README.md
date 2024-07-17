### Updated `README.md`

```markdown
# VDI Data Transfer Script

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
  - [Prerequisites](#prerequisites)
  - [Setup](#setup)
- [Usage](#usage)
  - [Command-Line Options](#command-line-options)
  - [Examples](#examples)
    - [Text Mode](#text-mode)
    - [Spreadsheet Mode](#spreadsheet-mode)
    - [Image Mode](#image-mode)
    - [Code Mode](#code-mode)
- [Configuration](#configuration)
- [Developer Information](#developer-information)
  - [Setup and Installation](#setup-and-installation)
  - [Explanation of Focus Requirement](#explanation-of-focus-requirement)
  - [Platform Compatibility](#platform-compatibility)
- [Potential Enhancements](#potential-enhancements)
- [Contributing](#contributing)

## Introduction

The VDI Data Transfer Script is a Python-based tool designed to facilitate the transfer of data to a Virtual Desktop Infrastructure (VDI) environment. This script uses `xdotool` to interact with a specified window on a Linux system, sending text, spreadsheet data, images, or code from the local machine to the VDI. It automates repetitive tasks, ensures data consistency, and improves productivity.

## Features

- **Text Mode**: Send text data to a target window.
- **Spreadsheet Mode**: Send data in a comma-separated format to a target window, simulating spreadsheet entries.
- **Image Mode**: Send image data to the target window by encoding it as text.
- **Code Mode**: Send code data to Visual Studio Code.
- **Clipboard Integration**: Use clipboard contents as input for text, spreadsheet, image, or code data.
- **Debug Logging**: Provides detailed debug logs for troubleshooting and monitoring script execution.

## Installation

### Prerequisites

Ensure you have Python 3 and `xdotool` installed on your system.

```bash
sudo apt-get install xdotool
```

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/your-username/vdi-data-transfer.git
   cd vdi-data-transfer
   ```

2. Set up a virtual environment:
   ```bash
   python3 -m venv vdi-env
   source vdi-env/bin/activate
   ```

3. Install the required Python libraries:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

To use the script, run the following command:
```bash
/usr/bin/python3 /path/to/paste_to_vdi.py [options] [path_to_file]
```

### Command-Line Options

- `-s`: Spreadsheet mode
- `-t`: Text editor mode
- `-i`: Image transfer mode
- `-e`: Code editor mode (Visual Studio Code)
- `-w <window_title>`: Specify the title of the target window (optional)
- `-c`: Use clipboard contents as input (no file needed)
- `-d`: Enable debug logging
- `-h`: Display the help message

### Examples

#### Text Mode

- **With File Input**:
  ```bash
  /usr/bin/python3 /path/to/paste_to_vdi.py -t -w "vdi_window_title - Brave" /path/to/textfile.txt
  ```

- **With Clipboard Input**:
  ```bash
  /usr/bin/python3 /path/to/paste_to_vdi.py -t -w "vdi_window_title - Brave" -c
  ```

#### Spreadsheet Mode

- **With File Input**:
  ```bash
  /usr/bin/python3 /path/to/paste_to_vdi.py -s -w "vdi_window_title - Brave" /path/to/spreadsheetfile.csv
  ```

- **With Clipboard Input**:
  ```bash
  /usr/bin/python3 /path/to/paste_to_vdi.py -s -w "vdi_window_title - Brave" -c
  ```

#### Image Mode

- **With File Input**:
  ```bash
  /usr/bin/python3 /path/to/paste_to_vdi.py -i -w "vdi_window_title - Brave" /path/to/imagefile.png
  ```

- **With Clipboard Input**:
  ```bash
  /usr/bin/python3 /path/to/paste_to_vdi.py -i -w "vdi_window_title - Brave" -c
  ```

#### Code Mode

- **With File Input**:
  ```bash
  /usr/bin/python3 /path/to/paste_to_vdi.py -e -w "vdi_window_title - Brave" /path/to/codefile.py
  ```

- **With Clipboard Input**:
  ```bash
  /usr/bin/python3 /path/to/paste_to_vdi.py -e -w "vdi_window_title - Brave" -c
  ```

## Configuration

### .env File

The `.env` file is used to configure various parameters for the script. Below is an example of a `.env` file:

```ini
WINDOW_TITLE="vdi_window_title - Brave"
DELAY_BETWEEN_KEYS=0.05
DELAY_BETWEEN_COMMANDS=0.2
DELAY_BETWEEN_APPLICATIONS=1
NOTEPAD_LOAD_TIME=2
EXCEL_LOAD_TIME=5
VSCODE_LOAD_TIME=3
CHUNK_SIZE=5
DELAY_BETWEEN_CHUNKS=0.5
```

### Parameters

- `WINDOW_TITLE`: The title of the target window where the data will be sent.
- `DELAY_BETWEEN_KEYS`: The delay (in seconds) between sending each key.
- `DELAY_BETWEEN_COMMANDS`: The delay (in seconds) between sending each command.
- `DELAY_BETWEEN_APPLICATIONS`: The delay (in seconds) between opening applications.
- `NOTEPAD_LOAD_TIME`: The time (in seconds) to wait for Notepad to load.
- `EXCEL_LOAD_TIME`: The time (in seconds) to wait for Excel to load.
- `VSCODE_LOAD_TIME`: The time (in seconds) to wait for Visual Studio Code to load.
- `CHUNK_SIZE`: The number of characters to send at a time.
- `DELAY_BETWEEN_CHUNKS`: The delay (in seconds) between sending chunks of characters.

## Developer Information

### Setup and Installation

Refer to the [Installation](#installation) section for setting up the environment. Ensure you have Python 3, `xdotool`, and the required Python libraries installed.

### Explanation of Focus Requirement

The target window must stay in focus during the operation to ensure that the keystrokes are correctly sent to the intended window. Losing focus can result in keystrokes being sent to the wrong window, causing unintended behavior. This is particularly crucial for applications like Excel or Notepad, where precise input is required.

### Platform Compatibility

This script is designed to work on Linux systems using `xdotool`. It will not work on Windows systems due to the lack of support for `xdotool`. To make it work on Windows, you would need to use equivalent tools or libraries such as `pywin32` or `ctypes` to interact with windows and send keystrokes.

## Potential Enhancements

- **Windows Support**: Implementing the functionality using Windows-specific libraries to send keystrokes and interact with windows.
- **MacOS Support**: Using `osascript` or other macOS-specific tools to achieve similar functionality.
- **Error Handling**: Improving error handling and recovery mechanisms for better resilience during execution.

## Contributing

Contributions are welcome to extend the functionality to other operating systems and improve error handling. If you have expertise in Windows or macOS automation, your input would be invaluable.

---

By following this documentation, you can set up and use the VDI Data Transfer Script effectively, whether you are a user or a developer looking to enhance the tool.
```
