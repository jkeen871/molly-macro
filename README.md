# Molly-macro

## Table of Contents
1. [Introduction](#introduction)
2. [Developer Information](#developer-information)
3. [Installation](#installation)
4. [User Interface](#user-interface)
   - [Main Window](#main-window)
   - [Configuration Selection](#configuration-selection)
   - [Input Method](#input-method)
   - [Window Selection](#window-selection)
   - [Debug Mode](#debug-mode)
   - [Command Preview](#command-preview)
   - [Progress Tracking](#progress-tracking)
   - [Content Viewer](#content-viewer)
5. [Configuration File (config.json)](#configuration-file-configjson)
   - [Structure](#structure)
   - [Application Configuration](#application-configuration)
   - [Open Steps](#open-steps)
   - [Example Configuration](#example-configuration)
6. [How Molly-macro Works](#how-molly-macro-works)
   - [Command-line Arguments](#command-line-arguments)
   - [Execution Flow](#execution-flow)
   - [Window Management](#window-management)
   - [Data Transfer](#data-transfer)
7. [Use Cases and Examples](#use-cases-and-examples)
8. [Linux Compatibility](#linux-compatibility)
9. [Windows Adaptation](#windows-adaptation)
10. [Troubleshooting](#troubleshooting)
11. [Contributing](#contributing)
12. [License](#license)

## Introduction

Molly-macro is a sophisticated data transfer tool designed to automate the process of inputting data into various applications. It provides both a graphical user interface for easy operation and a command-line interface for advanced users and automation scenarios. Molly-macro is particularly useful in environments where traditional clipboard operations or file imports are restricted or unavailable.

## Developer Information

- **Developer:** Jerry Keen
- **Email:** jkeen871@gmail.com

## Installation

1. Ensure you have Python 3.6 or later installed on your Linux system.
2. Clone the Molly-macro repository:
   ```
   git clone https://github.com/yourusername/molly-macro.git
   ```
3. Navigate to the project directory:
   ```
   cd molly-macro
   ```
4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## User Interface

### Main Window

The main window of Molly-macro provides a user-friendly interface for configuring and executing data transfers. It consists of several key components:

### Configuration Selection

- A dropdown menu allows users to select from pre-defined configurations stored in the config.json file.
- Each configuration represents a set of parameters for a specific application or scenario.
- Users can edit existing configurations or create new ones using the "Edit Config" button.

### Input Method

- Users can choose between using clipboard content or a file as the data source.
- A checkbox toggles between these two options.
- When "Use Clipboard" is unchecked, a file selection field and browse button become available.

### Window Selection

- A dropdown menu lists all currently open windows.
- Users select the target window for the data transfer.
- A "Refresh" button updates the list of available windows.

### Debug Mode

- A checkbox enables debug logging for troubleshooting purposes.
- When enabled, detailed logs are generated during the transfer process.

### Command Preview

- Displays the command that will be executed based on the current settings.
- Updates in real-time as users modify options.

### Progress Tracking

- A progress bar shows the status of the ongoing transfer.
- Percentage completion is displayed numerically.
- The current status (e.g., "Running", "Completed") is shown in a status bar.

### Content Viewer

- A "View Content" button opens a new window displaying the content to be transferred.
- Supports both clipboard and file content.
- Content is displayed in a scrollable, formatted text area.

## Configuration File (config.json)

The config.json file is a crucial component of Molly-macro, containing detailed configurations for various applications and scenarios. This file allows users to customize the behavior of Molly-macro for different target applications.

### Structure

The config.json file has the following high-level structure:

```json
{
  "applications": {
    "app_name_1": {
      // Application-specific configuration
    },
    "app_name_2": {
      // Application-specific configuration
    }
    // ... more applications ...
  }
}
```

### Application Configuration

Each application configuration can include the following fields:

- `type` (string): Specifies whether the application is "local" or "vdi" (Virtual Desktop Infrastructure).
- `mode` (string): Defines the input mode, e.g., "text", "spreadsheet", "code".
- `WINDOW_TITLE` (string): The title pattern to match for identifying the application window.
- `DELAY_BETWEEN_KEYS` (float): Time delay (in seconds) between individual keystrokes.
- `DELAY_BETWEEN_COMMANDS` (float): Time delay (in seconds) between separate commands or actions.
- `APP_LOAD_TIME` (float): Time (in seconds) to wait for the application to load after launching.
- `CHUNK_SIZE` (integer): Number of characters to send in each chunk during data transfer.
- `DELAY_BETWEEN_CHUNKS` (float): Time delay (in seconds) between sending chunks of data.
- `launch_command` (string, optional): Command to launch the application (for local applications).
- `window_match` (string): Pattern to match when searching for the application window.
- `no_payload` (boolean): If true, no data will be sent (useful for applications that only need to be opened).

### Open Steps

The `open_steps` array defines a series of actions to be performed after the application window is found or launched. Each step is an object with the following properties:

- `action` (string): The type of action to perform. Can be "key" (send a keystroke), "type" (type a string), "launch_window" (launch the application), or "raise_window" (bring the window to the foreground).
- `value` (string): The value associated with the action (e.g., the key to press or the string to type).

### Example Configuration

Here's a detailed example of a configuration for a text editor application:

```json
{
  "applications": {
    "gnome_text_editor": {
      "type": "local",
      "mode": "text",
      "WINDOW_TITLE": "Text Editor",
      "DELAY_BETWEEN_KEYS": 0.05,
      "DELAY_BETWEEN_COMMANDS": 0.1,
      "APP_LOAD_TIME": 3.0,
      "CHUNK_SIZE": 20,
      "DELAY_BETWEEN_CHUNKS": 0.2,
      "launch_command": "gnome-text-editor -s",
      "window_match": "Text Editor",
      "no_payload": false,
      "open_steps": [
        {
          "action": "launch_window",
          "value": ""
        },
        {
          "action": "raise_window",
          "value": ""
        },
        {
          "action": "key",
          "value": "ctrl+n"
        }
      ]
    }
  }
}
```

In this example:
- The application is a local GNOME Text Editor.
- It operates in text mode.
- There are specific delays defined for various operations.
- The application is launched using the `gnome-text-editor -s` command.
- After launching, it waits 3 seconds for the app to load.
- The open steps launch the window, bring it to the foreground, and then open a new document (Ctrl+N).

## How Molly-macro Works

Molly-macro operates by simulating keyboard input to transfer data into target applications. It uses a combination of Python scripts and system utilities to achieve this automation.

### Command-line Arguments

The core functionality is implemented in `molly-macro.py`, which accepts several command-line arguments:

- `-s`: Spreadsheet mode
- `-t`: Text editor mode
- `-i`: Image transfer mode (placeholder for future implementation)
- `-e`: Code editor mode
- `-w <window_id>`: Specify the target window ID
- `-c`: Use clipboard contents as input
- `-d`: Enable debug logging
- `--config <path>`: Path to the JSON configuration file
- `--config_name <name>`: Name of the configuration to use
- `--local`: Indicate that this is a local configuration
- `<path_to_file>`: Path to the input file (when not using clipboard)

### Execution Flow

1. Parse command-line arguments and load the specified configuration from config.json.
2. Identify or launch the target application window using the `window_match` pattern.
3. Execute any specified "open steps" to prepare the application.
4. Read input data from the clipboard or specified file.
5. Transfer the data to the target window using simulated keystrokes, respecting the `CHUNK_SIZE` and various delay settings.
6. Report progress and completion status.

### Window Management

Molly-macro uses the `xdotool` utility to interact with windows in the X Window System. It can:

- Search for windows by title or other attributes using the `window_match` pattern.
- Activate, focus, and raise windows.
- Send keystrokes to specific windows, adhering to the `DELAY_BETWEEN_KEYS` setting.

### Data Transfer

The data transfer process is chunk-based to handle large volumes of data efficiently:

1. The input is divided into manageable chunks based on the `CHUNK_SIZE` setting.
2. Each chunk is sent to the target window using simulated keystrokes.
3. Delays between chunks (`DELAY_BETWEEN_CHUNKS`) and keystrokes (`DELAY_BETWEEN_KEYS`) are applied to accommodate different application behaviors.

## Use Cases and Examples

1. **Transferring spreadsheet data to a VDI environment:**
   ```
   python molly-macro.py -s -c --config_name excel_vdi
   ```
   This command transfers clipboard content to an Excel application in a VDI environment using the "excel_vdi" configuration.

2. **Inputting code into a local IDE:**
   ```
   python molly-macro.py -e --config_name vscode --local /path/to/code.py
   ```
   This command inputs the contents of `code.py` into a local Visual Studio Code instance, using the settings defined in the "vscode" configuration.

3. **Transferring text to a remote text editor:**
   ```
   python molly-macro.py -t -w 12345678 --config_name remote_notepad
   ```
   This command sends clipboard content to a specific window (ID: 12345678) using the "remote_notepad" configuration.

## Linux Compatibility

Molly-macro is designed specifically for Linux systems due to its reliance on X Window System utilities, particularly `xdotool`. These tools provide low-level access to window management and input simulation, which are crucial for Molly-macro's functionality.

## Windows Adaptation

To adapt Molly-macro for Windows, several key changes would be necessary:

1. Replace `xdotool` functionality with Windows-equivalent APIs (e.g., Win32 API or UI Automation).
2. Modify window management code to use Windows-specific methods for finding, activating, and focusing windows.
3. Implement an alternative method for simulating keystrokes, possibly using the `SendInput` function or similar Windows APIs.
4. Adjust the configuration structure in config.json to accommodate Windows-specific parameters and behaviors.
5. Update file path handling and environment variable usage to align with Windows conventions.

These changes would require significant refactoring and testing to ensure compatibility and performance on Windows systems.

## Troubleshooting

- **Window not found:** Ensure the target application is running and visible. Try refreshing the window list or adjusting the `window_match` pattern in the configuration.
- **Transfer not starting:** Check that you have the necessary permissions to interact with the target window. Some applications or system settings may prevent automated input.
- **Incomplete transfers:** Adjust the timing parameters (`DELAY_BETWEEN_KEYS`, `DELAY_BETWEEN_CHUNKS`) in the configuration. Some applications may require longer delays between keystrokes or chunks.
- **Garbled output:** Verify that the input encoding matches the target application's expectations. You may need to modify the input preprocessing in extreme cases.

## Contributing

Contributions to Molly-macro are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Commit your changes with clear, descriptive messages.
4. Push your branch and submit a pull request.

Please ensure your code adheres to the project's styling guidelines and includes appropriate documentation and tests.

## License

Molly-macro is released under the MIT License. See the LICENSE file in the repository for full details.
