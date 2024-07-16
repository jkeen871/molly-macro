### README.md

# VDI Data Transfer Script

## Table of Contents

- [Introduction](#introduction)
- [Features](#features)
- [Installation](#installation)
- [Usage](#usage)
  - [Text Mode](#text-mode)
  - [Spreadsheet Mode](#spreadsheet-mode)
  - [Image Mode](#image-mode)
- [Developer Information](#developer-information)
  - [Setup and Installation](#setup-and-installation)
  - [Explanation of Focus Requirement](#explanation-of-focus-requirement)
  - [Platform Compatibility](#platform-compatibility)
- [Potential Enhancements](#potential-enhancements)
- [Contributing](#contributing)

## Introduction

The VDI Data Transfer Script is a Python-based tool designed to facilitate the transfer of data to a Virtual Desktop Infrastructure (VDI) environment. This script uses `xdotool` to interact with a specified window on a Linux system, sending text or image data from the local machine to the VDI. It automates repetitive tasks, ensures data consistency, and improves productivity.

## Features

- **Text Mode**: Send text data to a target window.
- **Spreadsheet Mode**: Send data in a comma-separated format to a target window, simulating spreadsheet entries.
- **Image Mode**: Send image data to the target window by encoding it as text.
- **Clipboard Integration**: Use clipboard contents as input for text or image data.
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
- `-w <window_title>`: Specify the title of the target window (optional)
- `-c`: Use clipboard contents as input (no file needed)
- `-d`: Enable debug logging
- `-h`: Display the help message

### Examples

#### Text Mode

- **With File Input**:
  ```bash
  /usr/bin/python3 /path/to/paste_to_vdi.py -t -w "NextGen VDI - Brave" /path/to/textfile.txt
  ```

- **With Clipboard Input**:
  ```bash
  /usr/bin/python3 /path/to/paste_to_vdi.py -t -w "NextGen VDI - Brave" -c
  ```

#### Spreadsheet Mode

- **With File Input**:
  ```bash
  /usr/bin/python3 /path/to/paste_to_vdi.py -s -w "NextGen VDI - Brave" /path/to/spreadsheetfile.csv
  ```

- **With Clipboard Input**:
  ```bash
  /usr/bin/python3 /path/to/paste_to_vdi.py -s -w "NextGen VDI - Brave" -c
  ```

#### Image Mode

- **With File Input**:
  ```bash
  /usr/bin/python3 /path/to/paste_to_vdi.py -i -w "NextGen VDI - Brave" /path/to/imagefile.png
  ```

- **With Clipboard Input**:
  ```bash
  /usr/bin/python3 /path/to/paste_to_vdi.py -i -w "NextGen VDI - Brave" -c
  ```

## Developer Information

### Setup and Installation

Refer to the [Installation](#installation) section for setting up the environment. Ensure you have Python 3, `xdotool`, and the required Python libraries installed.

### Explanation of Focus Requirement

The target window must stay in focus during the operation to ensure that the keystrokes are correctly sent to the intended window. Losing focus can result in keystrokes being sent to the wrong window, causing unintended behavior. This is particularly crucial for applications like Excel or Notepad, where precise input is required.

### Platform Compatibility

This script is designed to work on Linux systems using `xdotool`. It will not work on Windows systems due to the lack of support for `xdotool`. To make it work on Windows, you would need to use equivalent tools or libraries such as `pywin32` or `ctypes` to interact with windows and send keystrokes.

### Potential Enhancements

- **Windows Support**: Implementing the functionality using Windows-specific libraries to send keystrokes and interact with windows.
- **MacOS Support**: Using `osascript` or other macOS-specific tools to achieve similar functionality.
- **Error Handling**: Improving error handling and recovery mechanisms for better resilience during execution.

## Contributing

Contributions are welcome to extend the functionality to other operating systems and improve error handling. If you have expertise in Windows or macOS automation, your input would be invaluable.

---

By following this documentation, you can set up and use the VDI Data Transfer Script effectively, whether you are a user or a developer looking to enhance the tool.
