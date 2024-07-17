import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import subprocess
import sys
import os
import threading
import queue
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class VDIDataTransferGUI:
    """
    A class to create and manage the GUI for the VDI Data Transfer tool.

    This class encapsulates all the GUI elements and their associated functionality,
    including running the paste_to_vdi.py script and monitoring its progress.
    """

    def __init__(self, master):
        """
        Initialize the GUI window and its components.

        Args:
            master (tk.Tk): The root window of the application.

        Returns:
            None

        This method sets up the main window and initializes all GUI components.
        It also sets up the necessary variables for managing the script execution
        and progress tracking.
        """
        self.master = master
        master.title("VDI Data Transfer")
        master.geometry("400x600")

        self.process = None
        self.progress_queue = queue.Queue()
        self.should_update_progress = False

        self._create_widgets()
        self._bind_events()

        logger.info("GUI initialized")

    def _create_widgets(self):
        """
        Create and place all GUI widgets.

        Args:
            None

        Returns:
            None

        This method creates all the GUI elements, including mode selection,
        file selection, window title entry, checkboxes, buttons, progress bar,
        and status bar.
        """
        self._create_mode_selection()
        self._create_file_selection()
        self._create_window_title_entry()
        self._create_clipboard_checkbox()
        self._create_debug_checkbox()
        self._create_run_stop_buttons()
        self._create_command_preview()
        self._create_progress_bar()
        self._create_status_bar()

        logger.debug("All widgets created")

    def _create_mode_selection(self):
        """
        Create the mode selection radio buttons.

        Args:
            None

        Returns:
            None

        This method creates radio buttons for selecting the transfer mode
        (Text, Spreadsheet, Image, Code).
        """
        self.mode_label = ttk.Label(self.master, text="Select Mode:")
        self.mode_label.pack(pady=10)

        self.mode_var = tk.StringVar()
        modes = [("Text", "-t"), ("Spreadsheet", "-s"), ("Image", "-i"), ("Code", "-e")]
        for text, mode in modes:
            ttk.Radiobutton(self.master, text=text, variable=self.mode_var, value=mode).pack()

        logger.debug("Mode selection radio buttons created")

    def _create_file_selection(self):
        """
        Create the file selection entry and browse button.

        Args:
            None

        Returns:
            None

        This method creates an entry field for the file path and a button
        to open a file dialog for selecting a file.
        """
        self.file_frame = ttk.Frame(self.master)
        self.file_frame.pack(pady=10)

        self.file_label = ttk.Label(self.file_frame, text="File:")
        self.file_label.pack(side=tk.LEFT)

        self.file_entry = ttk.Entry(self.file_frame, width=30)
        self.file_entry.pack(side=tk.LEFT)

        self.file_button = ttk.Button(self.file_frame, text="Browse", command=self.browse_file)
        self.file_button.pack(side=tk.LEFT)

        logger.debug("File selection widgets created")

    def _create_window_title_entry(self):
        """
        Create the window title entry field.

        Args:
            None

        Returns:
            None

        This method creates an entry field for specifying the target window title.
        """
        self.window_frame = ttk.Frame(self.master)
        self.window_frame.pack(pady=10)

        self.window_label = ttk.Label(self.window_frame, text="Window Title:")
        self.window_label.pack(side=tk.LEFT)

        self.window_entry = ttk.Entry(self.window_frame, width=30)
        self.window_entry.pack(side=tk.LEFT)

        logger.debug("Window title entry created")

    def _create_clipboard_checkbox(self):
        """
        Create the 'Use Clipboard' checkbox.

        Args:
            None

        Returns:
            None

        This method creates a checkbox for toggling the use of clipboard content.
        """
        self.clipboard_var = tk.BooleanVar()
        self.clipboard_check = ttk.Checkbutton(self.master, text="Use Clipboard", variable=self.clipboard_var)
        self.clipboard_check.pack(pady=10)

        logger.debug("Clipboard checkbox created")

    def _create_debug_checkbox(self):
        """
        Create the 'Enable Debug Logging' checkbox.

        Args:
            None

        Returns:
            None

        This method creates a checkbox for enabling debug logging.
        """
        self.debug_var = tk.BooleanVar()
        self.debug_check = ttk.Checkbutton(self.master, text="Enable Debug Logging", variable=self.debug_var)
        self.debug_check.pack(pady=10)

        logger.debug("Debug logging checkbox created")

    def _create_run_stop_buttons(self):
        """
        Create the 'Run' and 'Stop' buttons.

        Args:
            None

        Returns:
            None

        This method creates buttons for running and stopping the script execution.
        """
        self.button_frame = ttk.Frame(self.master)
        self.button_frame.pack(pady=20)

        self.run_button = ttk.Button(self.button_frame, text="Run", command=self.run_script)
        self.run_button.pack(side=tk.LEFT, padx=10)

        self.stop_button = ttk.Button(self.button_frame, text="Stop", command=self.stop_script, state=tk.DISABLED)
        self.stop_button.pack(side=tk.LEFT, padx=10)

        logger.debug("Run and Stop buttons created")

    def _create_command_preview(self):
        """
        Create the command preview display.

        Args:
            None

        Returns:
            None

        This method creates a read-only entry widget to display the command
        that will be executed.
        """
        self.command_label = ttk.Label(self.master, text="Command Preview:")
        self.command_label.pack(pady=5)
        self.command_preview = ttk.Entry(self.master, width=50, state="readonly")
        self.command_preview.pack(pady=5)

        logger.debug("Command preview widget created")

    def _create_progress_bar(self):
        """
        Create the progress bar and percentage label.

        Args:
            None

        Returns:
            None

        This method creates a progress bar to show the script execution progress
        and a label to display the percentage.
        """
        self.progress_frame = ttk.Frame(self.master)
        self.progress_frame.pack(pady=10, padx=20, fill=tk.X)

        self.progress_bar = ttk.Progressbar(self.progress_frame, length=300, mode='determinate')
        self.progress_bar.pack(side=tk.LEFT, expand=True, fill=tk.X)

        self.progress_label = ttk.Label(self.progress_frame, text="0%")
        self.progress_label.pack(side=tk.RIGHT)

        logger.debug("Progress bar and label created")

    def _create_status_bar(self):
        """
        Create the status bar.

        Args:
            None

        Returns:
            None

        This method creates a status bar at the bottom of the GUI to display
        current operation status.
        """
        self.status_bar = ttk.Label(self.master, text="Ready", relief=tk.SUNKEN, anchor=tk.W)
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        logger.debug("Status bar created")

    def _bind_events(self):
        """
        Bind events to update the command preview.

        Args:
            None

        Returns:
            None

        This method binds various GUI events to the command preview update function.
        """
        self.mode_var.trace("w", self.update_command_preview)
        self.file_entry.bind("<KeyRelease>", self.update_command_preview)
        self.window_entry.bind("<KeyRelease>", self.update_command_preview)
        self.clipboard_var.trace("w", self.update_command_preview)
        self.debug_var.trace("w", self.update_command_preview)

        logger.debug("Events bound to command preview update")

    def browse_file(self):
        """
        Open a file dialog and update the file entry with the selected file path.

        Args:
            None

        Returns:
            None

        This method opens a file dialog, allows the user to select a file,
        and updates the file entry with the selected file path.
        """
        filename = filedialog.askopenfilename()
        self.file_entry.delete(0, tk.END)
        self.file_entry.insert(0, filename)
        self.update_command_preview()
        logger.debug(f"Selected file: {filename}")

    def update_command_preview(self, *args):
        """
        Update the command preview based on the current GUI state.

        Args:
            *args: Variable length argument list (not used, required for Tkinter callbacks)

        Returns:
            None

        This method is called whenever the user changes any option in the GUI.
        It constructs the command that will be used to run the paste_to_vdi.py script.
        """
        command = [sys.executable, "paste_to_vdi.py"]
        mode = self.mode_var.get()
        file_path = self.file_entry.get()
        window_title = self.window_entry.get()
        use_clipboard = self.clipboard_var.get()
        debug_mode = self.debug_var.get()

        if mode:
            command.append(mode)

        if window_title:
            command.extend(["-w", window_title])

        if use_clipboard:
            command.append("-c")

        if debug_mode:
            command.append("-d")

        if file_path and not use_clipboard:
            command.append(file_path)

        command_str = " ".join(command)
        self.command_preview.config(state="normal")
        self.command_preview.delete(0, tk.END)
        self.command_preview.insert(0, command_str)
        self.command_preview.config(state="readonly")
        logger.debug(f"Updated command preview: {command_str}")

    def run_script(self):
        """
        Execute the paste_to_vdi.py script with the current options.

        Args:
            None

        Returns:
            None

        This method is called when the user clicks the 'Run' button.
        It disables the 'Run' button, enables the 'Stop' button, and starts
        the script execution in a separate thread.
        """
        command = self.command_preview.get().split()

        if not self.mode_var.get():
            messagebox.showerror("Error", "Please select a mode.")
            return

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
                for line in iter(self.process.stdout.readline, ''):
                    line = line.strip()
                    if line.startswith("PROGRESS:"):
                        try:
                            progress = float(line.split(":")[1])
                            self.progress_queue.put(progress)
                            logger.debug(f"Received progress update: {progress:.2f}%")
                        except ValueError:
                            logger.error(f"Invalid progress value: {line}")
                    else:
                        logger.debug(f"Script output: {line}")
                self.process.wait()
                self.master.after(0, self.script_finished)
            except subprocess.CalledProcessError as e:
                logger.error(f"Script execution failed: {e}")
                self.master.after(0, lambda: self.script_failed(str(e)))
            finally:
                self.should_update_progress = False

        thread = threading.Thread(target=run_process)
        thread.start()

    def update_progress(self):
        """
        Update the progress bar, percentage label, and status bar.

        Args:
            None

        Returns:
            None

        This method is called periodically while the script is running.
        It checks for progress updates in the queue and updates the GUI accordingly.
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

        Args:
            None

        Returns:
            None

        This method is called when the user clicks the 'Stop' button.
        It terminates the script process and updates the GUI state.
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

        Args:
            None

        Returns:
            None

        This method is called when the script finishes execution without errors.
        It updates the GUI state and shows a success message.
        """
        logger.info("Script execution completed successfully")
        self.status_bar.config(text="Completed")
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_bar['value'] = 100
        self.progress_label['text'] = "100%"
        self.should_update_progress = False
        messagebox.showinfo("Success", "Script executed successfully.")

    def script_failed(self, error_message):
        """
        Handle script execution failure.

        Args:
            error_message (str): The error message from the script execution.

        Returns:
            None

        This method is called when the script fails to execute or encounters an error.
        It updates the GUI state and shows an error message.
        """
        logger.error(f"Script execution failed: {error_message}")
        self.status_bar.config(text="Failed")
        self.run_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        self.progress_bar['value'] = 0
        self.progress_label['text'] = "0%"
        self.should_update_progress = False
        messagebox.showerror("Error", f"Script execution failed: {error_message}")

def main():
    """
    Main function to initialize and run the GUI application.

    Args:
        None

    Returns:
        None

    This function creates the root Tkinter window, instantiates the VDIDataTransferGUI class,
    and starts the Tkinter event loop.
    """
    root = tk.Tk()
    gui = VDIDataTransferGUI(root)
    logger.info("Starting GUI application")
    root.mainloop()

if __name__ == "__main__":
    main()