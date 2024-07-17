# VDI Data Transfer Script

A Python-based tool for automating data transfer to Virtual Desktop Infrastructure (VDI) environments, now with a graphical user interface.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
  - [Command-Line Interface](#command-line-interface)
    - [Command-Line Options](#command-line-options)
    - [Examples](#examples)
  - [Graphical User Interface](#graphical-user-interface)
- [Configuration](#configuration)
- [Developer Guide](#developer-guide)
  - [Architecture](#architecture)
  - [Key Components](#key-components)
  - [Contributing](#contributing)
- [Troubleshooting](#troubleshooting)
- [License](#license)
- [Contact](#contact)

## Overview

The VDI Data Transfer Script is designed to streamline the process of transferring data to a Virtual Desktop Infrastructure (VDI) environment. It uses `xdotool` to interact with specified windows on a Linux system, enabling automated input of text, spreadsheet data, images, or code from a local machine to the VDI. The tool now includes both a command-line interface (`paste_to_vdi.py`) and a graphical user interface (`paste_to_vdi_gui.py`) for enhanced usability.

## Features

- **Multiple Transfer Modes**:
  - Text Mode: Send plain text to a target window
  - Spreadsheet Mode: Input data in a tabular format, simulating spreadsheet entries
  - Image Mode: Transfer image data by encoding it as text
  - Code Mode: Send code directly to Visual Studio Code
- **Clipboard Integration**: Use clipboard contents as input for any mode
- **Configurable Delays**: Customize timing between actions for optimal performance
- **Debug Logging**: Detailed logs for troubleshooting and execution monitoring
- **Graphical User Interface**: Easy-to-use GUI for configuring and executing transfers
- **Real-time Progress Tracking**: View transfer progress in the GUI

## Requirements

- Python 3.6+
- xdotool
- Linux operating system
- Additional Python packages: tkinter, pyautogui, pyperclip, python-dotenv

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/jkeen871/paste_to_vdi.git
   cd paste_to_vdi
   ```

2. Install xdotool:
   ```bash
   sudo apt-get install xdotool
   ```

3. Set up a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

4. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Install tkinter if not already available (required for GUI):
   ```bash
   sudo apt-get install python3-tk
   ```

## Usage

### Command-Line Interface

Run the script using the following command:

```bash
python paste_to_vdi.py [OPTIONS] [FILE]
```

#### Command-Line Options

- `-s`: Spreadsheet mode
- `-t`: Text editor mode
- `-i`: Image transfer mode
- `-e`: Code editor mode (Visual Studio Code)
- `-w TITLE`: Specify window title (default: "vdi_window_title - Brave")
- `-c`: Use clipboard contents as input
- `-d`: Enable debug logging

#### Examples

1. Send text file contents:
   ```bash
   python paste_to_vdi.py -t document.txt
   ```

2. Input spreadsheet data from clipboard:
   ```bash
   python paste_to_vdi.py -s -c
   ```

3. Transfer image with custom window title:
   ```bash
   python paste_to_vdi.py -i -w "My VDI Window" image.png
   ```

4. Send code to VS Code:
   ```bash
   python paste_to_vdi.py -e script.py
   ```

### Graphical User Interface

To launch the GUI, run:

```bash
python paste_to_vdi_gui.py
```

The GUI provides the following features:

1. **Mode Selection**: Choose between Text, Spreadsheet, Image, and Code modes.
2. **File Selection**: Browse and select input files or use clipboard content.
3. **Window Title**: Specify the target VDI window title.
4. **Debug Logging**: Enable or disable debug logging.
5. **Command Preview**: View the generated command before execution.
6. **Progress Tracking**: Monitor transfer progress with a progress bar and percentage indicator.
7. **Run/Stop Controls**: Start and stop transfers with dedicated buttons.

To use the GUI:

1. Select the desired transfer mode.
2. Choose a file or enable clipboard usage.
3. (Optional) Specify a custom window title.
4. (Optional) Enable debug logging.
5. Click "Run" to start the transfer.
6. Monitor progress in the status bar and progress bar.
7. Use the "Stop" button to terminate the transfer if needed.

## Configuration

Create a `.env` file in the project root to customize script behavior:

```ini
WINDOW_TITLE=vdi_window_title - Brave
DELAY_BETWEEN_KEYS=0.05
DELAY_BETWEEN_COMMANDS=0.2
DELAY_BETWEEN_APPLICATIONS=1
NOTEPAD_LOAD_TIME=2
EXCEL_LOAD_TIME=5
VSCODE_LOAD_TIME=3
CHUNK_SIZE=5
DELAY_BETWEEN_CHUNKS=0.5
```

Adjust these values to optimize performance for your specific VDI environment. The GUI will use these settings when executing transfers.

## Developer Guide

### Architecture

The project consists of two main components:

1. `paste_to_vdi.py`: The core script that handles data transfer operations.
2. `paste_to_vdi_gui.py`: A graphical user interface that wraps the functionality of `paste_to_vdi.py`.

Both scripts follow a modular design with separate functions for each major operation:

1. Window management (finding, activating)
2. Input simulation (keystrokes, clipboard operations)
3. Application-specific actions (opening Notepad, Excel, VS Code)
4. Data processing (chunking, encoding)

The GUI script uses threading to prevent UI freezing during transfers and implements a queue-based system for updating progress.

### Key Components

- `find_window_id()`: Locates the target window
- `send_command_to_window()`: Sends xdotool commands to the window
- `send_text_to_window()`: Handles text input, including special characters
- `send_line_spreadsheet()`: Manages spreadsheet data input
- `send_image()`: Processes and transfers image data
- `VDIDataTransferGUI`: Main class for the graphical user interface
- `update_progress()`: Handles real-time progress updates in the GUI

### Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b new-feature`
3. Commit your changes: `git commit -am 'Add new feature'`
4. Push to the branch: `git push origin new-feature`
5. Submit a pull request

Please ensure your code adheres to the existing style and includes appropriate tests and documentation.

## Troubleshooting

- **Window not found**: Verify the window title in your `.env` file matches exactly
- **Slow performance**: Adjust delay settings in the `.env` file
- **Incomplete transfers**: Increase `CHUNK_SIZE` for larger data transfers
- **Unexpected behavior**: Enable debug logging with `-d` for detailed execution information
- **GUI not responding**: Check the console output for error messages
- **Progress bar not updating**: Ensure `paste_to_vdi.py` is printing progress updates correctly

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Contact

For support or inquiries, please open an issue on the GitHub repository or contact the maintainer at jkeen871@gmail.com.
