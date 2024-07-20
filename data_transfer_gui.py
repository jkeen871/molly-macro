import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import sys
import json
import os
import logging
import queue
import threading
from edit_config_window import EditConfigWindow
from tooltip import ToolTip
from config_schema import CONFIG_SCHEMA
import shlex
import pyperclip
from content_viewer_window import ContentViewerWindow



# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s - %(message)s')
logger = logging.getLogger(__name__)

class DataTransferGUI:
    """
    A class to create and manage the GUI for the Data Transfer tool.

    This class encapsulates all the GUI elements and their associated functionality,
    including running the molly-macro.py script and monitoring its progress.
    """

    def __init__(self, master):
        self.master = master
        self.root = master  # Store reference to the root window
        master.title("Data Transfer")
        master.geometry("500x600")
        master.resizable(False, False)

        self.process = None
        self.progress_queue = queue.Queue()
        self.should_update_progress = False
        self.disabled_widgets = []  # List to keep track of disabled widgets

        self.windows = []  # This will store tuples of (window_name, window_id)
        self.selected_window_id = None  # This will store the selected window ID

        self.load_config()
        self._create_widgets()
        self._bind_events()
        self.refresh_configurations()
        self.refresh_windows()

        logger.info("GUI initialized")

    def load_config(self):
        """
        Load the configuration file and environment variables.

        This method loads the configuration from a JSON file and the environment file,
        updating the configuration with default values where necessary.
        """
        try:
            with open("config.json", "r") as file:
                self.config = json.load(file)
            logger.info("Configuration loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            self.config = {}

        # Load environment variables
        self.env_config = {}
        try:
            with open(".env", "r") as file:
                for line in file:
                    parts = line.strip().split('=')
                    if len(parts) == 2:
                        key, value = parts
                        self.env_config[key] = value
            logger.info("Environment variables loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load environment variables: {e}")

        # Apply default values from .env file if not present in the config
        for app, app_config in self.config.get("applications", {}).items():
            for key in ["WINDOW_TITLE", "DELAY_BETWEEN_KEYS", "DELAY_BETWEEN_COMMANDS", "DELAY_BETWEEN_APPLICATIONS",
                        "APP_LOAD_TIME", "CHUNK_SIZE", "DELAY_BETWEEN_CHUNKS"]:
                if key not in app_config and key in self.env_config:
                    app_config[key] = self.env_config[key]

    def _create_widgets(self):
        self._create_mode_selection()
        self._create_clipboard_checkbox()
        self._create_file_selection()
        self._create_window_title_entry()
        self._create_debug_checkbox()
        self._create_run_stop_buttons()
        self._create_command_preview()
        self._create_progress_bar()
        self._create_status_bar()

        # Add the Edit Config button
        self.edit_config_button = ttk.Button(self.master, text="Edit Config", command=self.edit_config)
        self.edit_config_button.pack(pady=10)
        ToolTip(self.edit_config_button, "Edit the selected configuration")

        # Add the View Content button
        self.view_content_button = ttk.Button(self.master, text="View Content", command=self.view_content)
        self.view_content_button.pack(pady=10)
        ToolTip(self.view_content_button, "View the contents of the clipboard or selected file")

        logger.debug("All widgets created")

    def _create_mode_selection(self):
        """
        Create the mode selection dropdown.
        """
        self.mode_label = ttk.Label(self.master, text="Select Configuration:")
        self.mode_label.pack(pady=10)

        self.selected_config = tk.StringVar()
        self.config_dropdown = ttk.Combobox(self.master, textvariable=self.selected_config)
        self.config_dropdown.pack(pady=10)
        ToolTip(self.config_dropdown, "Select a configuration for data transfer")

    def _create_file_selection(self):
        """
        Create the file selection entry and browse button.
        """
        self.file_frame = ttk.Frame(self.master)
        self.file_frame.pack(pady=10)

        self.file_label = ttk.Label(self.file_frame, text="File:")
        self.file_label.pack(side=tk.LEFT)

        self.file_entry = ttk.Entry(self.file_frame, width=30)
        self.file_entry.pack(side=tk.LEFT)
        ToolTip(self.file_entry, "Enter the path to the file")

        self.file_button = ttk.Button(self.file_frame, text="Browse", command=self.browse_file)
        self.file_button.pack(side=tk.LEFT)
        ToolTip(self.file_button, "Browse for a file")

        logger.debug("File selection widgets created")

        self.toggle_file_selection()  # Call the method to set the initial state based on the default checkbox value

    def _create_window_title_entry(self):
        self.window_frame = ttk.Frame(self.master)
        self.window_frame.pack(pady=10)

        self.window_label = ttk.Label(self.window_frame, text="Window:")
        self.window_label.pack(side=tk.LEFT)

        self.window_entry = ttk.Combobox(self.window_frame, width=30)
        self.window_entry.pack(side=tk.LEFT)
        self.window_entry.bind("<<ComboboxSelected>>", self.on_window_selected)
        ToolTip(self.window_entry, "Select the window for data transfer")

        self.refresh_button = ttk.Button(self.window_frame, text="Refresh", command=self.refresh_windows)
        self.refresh_button.pack(side=tk.LEFT)
        ToolTip(self.refresh_button, "Refresh the list of open windows")

        logger.debug("Window selection widgets created")

    def _create_clipboard_checkbox(self):
        """
        Create the 'Use Clipboard' checkbox.
        """
        self.clipboard_var = tk.BooleanVar(value=True)  # Set to True by default
        self.clipboard_check = ttk.Checkbutton(self.master, text="Use Clipboard", variable=self.clipboard_var,
                                               command=self.toggle_file_selection)
        self.clipboard_check.pack(pady=10)
        ToolTip(self.clipboard_check, "Use clipboard content for data transfer")

        logger.debug("Clipboard checkbox created")

    def toggle_file_selection(self):
        """
        Enable or disable the file selection entry and browse button based on the clipboard checkbox state.
        """
        if self.clipboard_var.get():
            self.file_entry.config(state=tk.DISABLED)
            self.file_button.config(state=tk.DISABLED)
        else:
            self.file_entry.config(state=tk.NORMAL)
            self.file_button.config(state=tk.NORMAL)

    def _create_debug_checkbox(self):
        """
        Create the 'Enable Debug Logging' checkbox.
        """
        self.debug_var = tk.BooleanVar()
        self.debug_check = ttk.Checkbutton(self.master, text="Enable Debug Logging", variable=self.debug_var)
        self.debug_check.pack(pady=10)
        ToolTip(self.debug_check, "Enable debug logging for detailed output")

        logger.debug("Debug logging checkbox created")

    def _create_run_stop_buttons(self):
        """
        Create the 'Run' and 'Stop' buttons.
        """
        self.button_frame = ttk.Frame(self.master)
        self.button_frame.pack(pady=20)

        self.run_button = ttk.Button(self.button_frame, text="Run", command=self.run_script)
        self.run_button.pack(side=tk.LEFT, padx=10)
        ToolTip(self.run_button, "Run the data transfer script")

        self.stop_button = ttk.Button(self.button_frame, text="Stop", command=self.stop_script, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)
        ToolTip(self.stop_button, "Stop the data transfer script")

        logger.debug("Run and Stop buttons created")

    def _create_command_preview(self):
        """
        Create the command preview display.
        """
        self.command_label = ttk.Label(self.master, text="Command Preview:")
        self.command_label.pack(pady=5)
        self.command_preview = ttk.Entry(self.master, width=50, state="readonly")
        self.command_preview.pack(pady=5)
        ToolTip(self.command_preview, "Preview of the command that will be executed")

        logger.debug("Command preview widget created")

    def _create_progress_bar(self):
        """
        Create the progress bar and percentage label.
        """
        self.progress_frame = ttk.Frame(self.master)
        self.progress_frame.pack(pady=10, padx=20, fill=tk.X)

        self.progress_bar = ttk.Progressbar(self.progress_frame, length=300, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, expand=True, fill=tk.X)
        ToolTip(self.progress_bar, "Progress of the data transfer")

        self.progress_label = ttk.Label(self.progress_frame, text="0%")
        self.progress_label.pack(side=tk.RIGHT)
        ToolTip(self.progress_label, "Percentage of data transferred")

        logger.debug("Progress bar and label created")

    def _create_status_bar(self):
        """
        Create the status bar.
        """
        self.status_bar = ttk.Label(self.master, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)
        ToolTip(self.status_bar, "Current status of the application")

        logger.debug("Status bar created")

    def _bind_events(self):
        """
        Bind events to update the command preview.
        """
        self.selected_config.trace("w", self.update_command_preview)
        self.file_entry.bind("<KeyRelease>", self.update_command_preview)
        self.window_entry.bind("<KeyRelease>", self.update_command_preview)
        self.clipboard_var.trace("w", self.update_command_preview)
        self.debug_var.trace("w", self.update_command_preview)

        logger.debug("Events bound to command preview update")

    def browse_file(self):
        """
        Open a file dialog and update the file entry with the selected file path.
        """
        filename = filedialog.askopenfilename()
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, filename)
        self.update_command_preview()
        logger.debug(f"Selected file: {filename}")

    def on_window_selected(self, event):
        selected_name = self.window_entry.get()
        self.selected_window_id = None  # Reset the selected window ID
        for name, win_id in self.windows:
            if name == selected_name:
                self.selected_window_id = win_id
                break
        logger.debug(f"Selected window: {selected_name}, ID: {self.selected_window_id}")
        self.update_command_preview()

    def update_command_preview(self, *args):
        config_name = self.selected_config.get()
        if not config_name:
            return

        command = [sys.executable, "molly-macro.py", "--config_name", shlex.quote(config_name), "--config",
                   "config.json"]

        app_config = self.config['applications'].get(config_name, {})
        mode = app_config.get('mode')
        if mode:
            mode_flags = {
                "text": "-t",
                "spreadsheet": "-s",
                "image": "-i",
                "code": "-e"
            }
            if mode in mode_flags:
                command.append(mode_flags[mode])
            else:
                logger.warning(f"Unknown mode '{mode}' in configuration")

            # Add window ID for non-local configurations or those without a launch command
        if app_config.get("type") != "local" or "launch_command" not in app_config:
            if self.selected_window_id:
                command.extend(["-w", self.selected_window_id])
            else:
                logger.warning("No window ID selected for non-local configuration")

        if self.clipboard_var.get():
            command.append("-c")

        if self.debug_var.get():
            command.append("-d")

        file_path = self.file_entry.get()
        if file_path and not self.clipboard_var.get():
            command.append(shlex.quote(file_path))

        command_str = " ".join(command)
        self.command_preview.config(state="normal")
        self.command_preview.delete(0, tk.END)
        self.command_preview.insert(0, command_str)
        self.command_preview.config(state="readonly")
        logger.debug(f"Updated command preview: {command_str}")
        logger.debug(f"Current selected window ID: {self.selected_window_id}")

    def run_script(self):
        config_name = self.selected_config.get()
        if not config_name:
            messagebox.showerror("Error", "Please select a configuration.")
            return

        app_config = self.config['applications'].get(config_name)
        if not app_config:
            messagebox.showerror("Error", "Selected configuration not found.")
            return

        command = shlex.split(self.command_preview.get())

        # Check if we need to add the window ID
        if app_config["type"] != "local" or "launch_command" not in app_config:
            if not self.selected_window_id:
                messagebox.showerror("Error", "No window selected.")
                return
            # Remove existing -w argument if present
            if "-w" in command:
                w_index = command.index("-w")
                del command[w_index:w_index + 2]
            # Add the correct window ID
            command.extend(["-w", self.selected_window_id])

        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_bar.config(text="Running...")
        self.progress_bar['value'] = 0
        self.progress_label['text'] = "0%"

        logger.info(f"Starting script execution: {' '.join(command)}")

        self.should_update_progress = True
        self.update_progress()  # Start progress updates

        def run_process():
            try:
                self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                universal_newlines=True, bufsize=1)

                stdout_thread = threading.Thread(target=self.handle_output, args=(self.process.stdout,))
                stderr_thread = threading.Thread(target=self.handle_output, args=(self.process.stderr,))
                stdout_thread.start()
                stderr_thread.start()

                self.process.wait()
                stdout_thread.join()
                stderr_thread.join()

                if self.process.returncode != 0:
                    self.master.after(0, lambda: self.show_error_popup(
                        f"Script exited with non-zero status: {self.process.returncode}"))
                else:
                    self.master.after(0, self.script_finished)
            except Exception as e:
                logger.error(f"Script execution failed: {e}")
                self.master.after(0, lambda: self.show_error_popup(str(e)))
            finally:
                self.should_update_progress = False

        thread = threading.Thread(target=run_process)
        thread.start()

    def view_content(self):
        if self.clipboard_var.get():
            content = pyperclip.paste()
            title = "Clipboard Content"
        else:
            file_path = self.file_entry.get()
            if not file_path:
                messagebox.showerror("Error", "No file selected.")
                return
            try:
                with open(file_path, 'r') as file:
                    content = file.read()
                title = f"File Content: {file_path}"
            except Exception as e:
                messagebox.showerror("Error", f"Failed to read file: {str(e)}")
                return

        ContentViewerWindow(self.master, title, content)


    def refresh_configurations(self):
        """
        Refresh the list of available configurations.

        This method updates the dropdown list of configurations based on the
        current configurations loaded from the config file.
        """
        configurations = sorted(list(self.config.get('applications', {}).keys()))  # Sort the configurations
        self.config_dropdown['values'] = configurations
        self.selected_config.set('')  # Clear the current selection
        logger.info("Configurations list refreshed")

    def refresh_windows(self):
        try:
            output = subprocess.check_output(["xdotool", "search", "--onlyvisible", "--name", "."]).decode("utf-8")
            window_ids = output.strip().split('\n')
            self.windows = []
            for win_id in window_ids:
                if win_id:
                    try:
                        name = subprocess.check_output(["xdotool", "getwindowname", win_id]).decode("utf-8").strip()
                        self.windows.append((name, win_id))
                    except subprocess.CalledProcessError:
                        pass  # Skip windows that can't be queried

            window_names = [name for name, _ in self.windows]
            self.window_entry['values'] = window_names
            logger.info(f"Windows list refreshed. Found {len(self.windows)} windows.")
            logger.debug(f"Windows: {self.windows}")
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to refresh windows: {e}")

    def run_script(self):
        config_name = self.selected_config.get()
        if not config_name:
            messagebox.showerror("Error", "Please select a configuration.")
            return

        app_config = self.config['applications'].get(config_name)
        if not app_config:
            messagebox.showerror("Error", "Selected configuration not found.")
            return

        command = shlex.split(self.command_preview.get())

        # Check if we need to add the window ID
        if app_config["type"] != "local" or "launch_command" not in app_config:
            if not self.selected_window_id:
                messagebox.showerror("Error", "No window selected.")
                return
            # Remove existing -w argument if present
            if "-w" in command:
                w_index = command.index("-w")
                del command[w_index:w_index + 2]
            # Add the correct window ID
            command.extend(["-w", self.selected_window_id])

        self.run_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.status_bar.config(text="Running...")
        self.progress_bar['value'] = 0
        self.progress_label['text'] = "0%"

        logger.info(f"Starting script execution: {' '.join(command)}")

        self.should_update_progress = True
        self.update_progress()  # Start progress updates

        def run_process():
            try:
                self.process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                                universal_newlines=True, bufsize=1)

                stdout_thread = threading.Thread(target=self.handle_output, args=(self.process.stdout,))
                stderr_thread = threading.Thread(target=self.handle_output, args=(self.process.stderr,))
                stdout_thread.start()
                stderr_thread.start()

                # Wait for the process to complete
                self.process.wait()

                # Wait for stdout and stderr to be fully processed
                stdout_thread.join()
                stderr_thread.join()

                # Check if the transfer was completed
                if self.transfer_completed:
                    self.master.after(0, self.script_finished)
                else:
                    self.master.after(0, lambda: self.show_error_popup("Transfer did not complete successfully"))

            except Exception as e:
                logger.error(f"Script execution failed: {e}")
                self.master.after(0, lambda: self.show_error_popup(str(e)))
            finally:
                self.should_update_progress = False

        thread = threading.Thread(target=run_process)
        thread.start()

    def handle_output(self, pipe):
        self.transfer_completed = False
        for line in iter(pipe.readline, ''):
            line = line.strip()
            if line.startswith("PROGRESS:"):
                try:
                    progress = float(line.split(":")[1])
                    self.progress_queue.put(progress)
                    if progress >= 100:
                        self.transfer_completed = True
                        logger.info("Transfer completed")
                except ValueError:
                    logger.error(f"Invalid progress value: {line}")
            elif line.startswith("ERROR:"):
                self.master.after(0, lambda: self.show_error_popup(line[6:]))
            else:
                logger.debug(f"Script output: {line}")

    def show_error_popup(self, error_message):
        """
        Display an error message in a popup window and reset the GUI state.
        """
        messagebox.showerror("Error", error_message)
        self.reset_gui_state()
        logger.error(f"Script execution failed: {error_message}")

    def update_progress(self):
        """
        Update the progress bar, percentage label, and status bar.
        """
        try:
            while not self.progress_queue.empty():
                progress = self.progress_queue.get_nowait()
                self.progress_bar['value'] = progress
                self.progress_label['text'] = f"{progress:.1f}%"
                self.status_bar.config(text=f"Running... {progress:.1f}% complete")
                logger.debug(f"Updated progress bar: {progress:.1f}%")
        except queue.Empty:
            pass

        if self.should_update_progress:
            self.master.after(100, self.update_progress)

    def stop_script(self):
        """
        Terminate the running script process.
        """
        if self.process:
            self.process.terminate()
            logger.info("Script execution terminated by user")
            self.status_bar.config(text="Stopped")
            self.run_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.should_update_progress = False

    def script_finished(self):
        """
        Handle the successful completion of the script.
        """
        logger.info("Script execution completed successfully")
        self.status_bar.config(text="Completed")
        self.should_update_progress = False

        # Display completion popup
        self.master.after(0, self.show_completion_popup)

    def show_completion_popup(self):
        """
        Display a popup indicating the transfer is complete and reset the GUI state after user acknowledgment.
        """
        if hasattr(self, 'warnings') and self.warnings:
            warning_message = "Transfer completed with warnings:\n\n" + "\n".join(self.warnings)
            messagebox.showwarning("Transfer Complete", warning_message)
        else:
            messagebox.showinfo("Transfer Complete", "Transfer completed successfully.")

        # Reset GUI state after user closes the popup
        self.reset_gui_state()

    def reset_gui_state(self):
        """
        Reset the GUI state after transfer completion.
        """
        self.status_bar.config(text="Ready")
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        self.progress_label['text'] = "0%"
        logger.debug("GUI state reset after transfer completion")

    def script_failed(self, error_message):
        """
        Handle script execution failure.
        """
        logger.error(f"Script execution failed: {error_message}")
        self.status_bar.config(text="Failed")
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        self.progress_label['text'] = "0%"
        self.should_update_progress = False

    def disable_main_window(self):
        """
        Disable all widgets in the main window that support the 'state' option.
        """
        for child in self.master.winfo_children():
            if child.winfo_class() != 'Toplevel':  # Don't disable child windows
                try:
                    current_state = child.cget('state')
                    if current_state != 'disabled':
                        child.configure(state='disabled')
                        self.disabled_widgets.append(child)
                except tk.TclError:
                    # This widget doesn't support the 'state' option, skip it
                    pass

        logger.debug("Main window widgets disabled")

    def enable_main_window(self):
        """
        Enable all previously disabled widgets in the main window.
        """
        for widget in self.disabled_widgets:
            try:
                if isinstance(widget, ttk.Combobox):
                    widget.configure(state='readonly')
                else:
                    widget.configure(state='normal')
            except tk.TclError:
                # This widget doesn't support the 'state' option, skip it
                pass
        self.disabled_widgets.clear()

        # Instead of using wm_attributes, we'll just focus on the main window
        self.master.focus_force()  # Force focus back to the main window
        self.master.update()  # Update the window to reflect changes

        logger.debug("Main window widgets enabled")

    def edit_config(self):
        """
        Open the edit configuration window.
        """
        config_name = self.selected_config.get()
        if not config_name:
            messagebox.showerror("Error", "Please select a configuration to edit.")
            return

        config_data = self.config['applications'][config_name]
        self.disable_main_window()
        EditConfigWindow(self.master, self, config_name, config_data, self.save_config)

    def save_config(self, config_name, config_data):
        # Validate and convert the config data
        validated_config = {}
        for key, value in config_data.items():
            if key in CONFIG_SCHEMA:
                try:
                    validated_config[key] = CONFIG_SCHEMA[key](value)
                except ValueError:
                    messagebox.showerror("Error", f"Invalid value for {key}. Expected {CONFIG_SCHEMA[key].__name__}.")
                    return
            else:
                validated_config[key] = value

        # Update the configuration in memory
        self.config['applications'][config_name] = validated_config

        # Save the updated configuration to the file
        with open("config.json", "w") as file:
            json.dump(self.config, file, indent=4)

        self.refresh_configurations()
        self.enable_main_window()
        logger.info(f"Configuration '{config_name}' saved successfully")

        # Update the selected configuration in the dropdown
        self.selected_config.set(config_name)


    if __name__ == "__main__":
        root = tk.Tk()
        app = DataTransferGUI(root)
        root.mainloop()