import tkinter as tk
from tkinter import ttk

class ContentViewerWindow(tk.Toplevel):
    def __init__(self, parent, title, content):
        super().__init__(parent)
        self.title(title)
        self.geometry("400x400")
        self.create_widgets(content)

    def create_widgets(self, content):
        # Create a frame to hold the text widget and scrollbar
        frame = ttk.Frame(self)
        frame.pack(expand=True, fill='both', padx=10, pady=10)

        # Create a text widget with scrollbar
        self.text_widget = tk.Text(frame, wrap='word', font=('TkDefaultFont', 10))
        self.text_widget.pack(side='left', expand=True, fill='both')

        scrollbar = ttk.Scrollbar(frame, orient='vertical', command=self.text_widget.yview)
        scrollbar.pack(side='right', fill='y')

        self.text_widget.config(yscrollcommand=scrollbar.set)

        # Insert the content into the text widget
        self.text_widget.insert('1.0', content)
        self.text_widget.config(state='disabled')  # Make it read-only

        # Create an OK button
        ok_button = ttk.Button(self, text="OK", command=self.destroy)
        ok_button.pack(pady=10)

    def show(self):
        self.grab_set()  # Make the window modal
        self.wait_window()  # Wait for the window to be closed