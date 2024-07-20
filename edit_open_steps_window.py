import tkinter as tk
from tkinter import ttk
from config_schema import OPEN_STEP_SCHEMA
import logging

logger = logging.getLogger(__name__)

ACTION_OPTIONS = {
    "key": "Send a single key press or key combination",
    "type": "Type a string of characters",
    "launch_window": "Launch an application window",
    "raise_window": "Bring an existing window to the foreground"
}

# List of common Ctrl and Alt key combinations and other special keys
SPECIAL_KEYS = [
    "ctrl+a", "ctrl+b", "ctrl+c", "ctrl+d", "ctrl+e", "ctrl+f", "ctrl+g", "ctrl+h", "ctrl+i", "ctrl+j",
    "ctrl+k", "ctrl+l", "ctrl+m", "ctrl+n", "ctrl+o", "ctrl+p", "ctrl+q", "ctrl+r", "ctrl+s", "ctrl+t",
    "ctrl+u", "ctrl+v", "ctrl+w", "ctrl+x", "ctrl+y", "ctrl+z",
    "alt+a", "alt+b", "alt+c", "alt+d", "alt+e", "alt+f", "alt+g", "alt+h", "alt+i", "alt+j",
    "alt+k", "alt+l", "alt+m", "alt+n", "alt+o", "alt+p", "alt+q", "alt+r", "alt+s", "alt+t",
    "alt+u", "alt+v", "alt+w", "alt+x", "alt+y", "alt+z",
    "ctrl+alt+a", "ctrl+alt+b", "ctrl+alt+c", "ctrl+alt+d", "ctrl+alt+e", "ctrl+alt+f",
    "ctrl+Escape", "alt+Tab", "ctrl+shift+Escape", "Return", "BackSpace", "Delete", "Insert",
    "Home", "End", "Page_Up", "Page_Down", "Up", "Down", "Left", "Right"
]

class AutocompleteCombobox(ttk.Combobox):
    def __init__(self, master=None, **kwargs):
        super().__init__(master, **kwargs)
        self._completion_list = []
        self.set_completion_list(kwargs.get('values', []))
        self.bind('<KeyRelease>', self.handle_keyrelease)

    def set_completion_list(self, completion_list):
        self._completion_list = sorted(completion_list, key=str.lower)
        self._hits = []
        self._hit_index = 0
        self.position = 0

    def autocomplete(self, delta=0):
        if delta:
            self.delete(self.position, tk.END)
        else:
            self.position = len(self.get())
        _hits = [item for item in self._completion_list if item.lower().startswith(self.get().lower())]
        if _hits != self._hits:
            self._hit_index = 0
            self._hits = _hits
        if _hits == self._hits and self._hits:
            self._hit_index = (self._hit_index + delta) % len(self._hits)
        if self._hits:
            self.delete(0, tk.END)
            self.insert(0, self._hits[self._hit_index])
            self.select_range(self.position, tk.END)

    def handle_keyrelease(self, event):
        if event.keysym == "BackSpace":
            self.delete(self.index(tk.INSERT), tk.END)
            self.position = self.index(tk.END)
        if event.keysym == "Left":
            if self.position < self.index(tk.END):
                self.delete(self.position, tk.END)
            else:
                self.position = self.position - 1
                self.delete(self.position, tk.END)
        if event.keysym == "Right":
            self.position = self.index(tk.END)
        if len(event.keysym) == 1:
            self.autocomplete()

class EditOpenStepsWindow(tk.Toplevel):
    def __init__(self, parent, config_name, open_steps, save_callback):
        super().__init__(parent)
        self.parent = parent
        self.config_name = config_name
        self.open_steps = open_steps or []
        self.save_callback = save_callback

        self.title(f"Edit Open Steps: {config_name}")
        self.geometry("600x500")
        self.resizable(False, False)
        self.entries = []

        self._create_widgets()

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.transient(parent)
        self.grab_set()

    def _create_widgets(self):
        self.step_frame = ttk.Frame(self)
        self.step_frame.pack(padx=10, pady=10, fill=tk.BOTH, expand=True)

        # Create headers
        ttk.Label(self.step_frame, text="Action").grid(row=0, column=0, padx=5, pady=5)
        ttk.Label(self.step_frame, text="Value").grid(row=0, column=1, padx=5, pady=5)

        for step in self.open_steps:
            self.add_step_widgets(step)

        self.add_button = ttk.Button(self, text="Add Step", command=self.add_step)
        self.add_button.pack(pady=10)

        self.save_button = ttk.Button(self, text="Save", command=self.save)
        self.save_button.pack(side=tk.LEFT, padx=(10, 5), pady=10)

        self.cancel_button = ttk.Button(self, text="Cancel", command=self.on_close)
        self.cancel_button.pack(side=tk.RIGHT, padx=(5, 10), pady=10)

    def add_step_widgets(self, step):
        row = len(self.entries) + 1
        action_var = tk.StringVar(value=step.get("action", ""))
        action_options = list(ACTION_OPTIONS.keys())
        action_menu = ttk.Combobox(self.step_frame, textvariable=action_var, values=action_options)
        action_menu.grid(row=row, column=0, padx=5, pady=5)

        value_var = tk.StringVar(value=step.get("value", ""))
        value_entry = AutocompleteCombobox(self.step_frame, textvariable=value_var, values=SPECIAL_KEYS)
        value_entry.grid(row=row, column=1, padx=5, pady=5)

        delete_button = ttk.Button(self.step_frame, text="-", command=lambda: self.delete_step(row))
        delete_button.grid(row=row, column=2, padx=5, pady=5)

        self.entries.append({"action": action_var, "value": value_var})

    def add_step(self):
        self.open_steps.append({"action": "", "value": ""})
        self.add_step_widgets({"action": "", "value": ""})

    def delete_step(self, index):
        del self.open_steps[index - 1]
        for widget in self.step_frame.grid_slaves():
            if int(widget.grid_info()["row"]) == index:
                widget.destroy()

        self.entries.pop(index - 1)
        for row, entry in enumerate(self.entries, start=1):
            entry["action"].widget.grid(row=row, column=0)
            entry["value"].widget.grid(row=row, column=1)
            self.step_frame.grid_slaves(row=row, column=2)[0].grid(row=row, column=2)

    def save(self):
        self.open_steps = [
            {
                "action": OPEN_STEP_SCHEMA["action"](entry["action"].get()),
                "value": OPEN_STEP_SCHEMA["value"](entry["value"].get())
            } for entry in self.entries
        ]
        self.save_callback(self.open_steps)
        self.on_close()

    def on_close(self):
        self.grab_release()
        self.destroy()

logger.info("EditOpenStepsWindow class defined")