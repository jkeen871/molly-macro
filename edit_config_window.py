import tkinter as tk
from tkinter import ttk, messagebox
import json
from config_schema import CONFIG_SCHEMA, OPEN_STEP_SCHEMA
from edit_open_steps_window import EditOpenStepsWindow
import logging
logger = logging.getLogger(__name__)


class EditConfigWindow(tk.Toplevel):
    def __init__(self, root, parent, config_name, config_data, save_callback):
        super().__init__(root)
        self.parent = parent
        self.original_config_name = config_name
        self.config_name = config_name
        self.config_data = config_data
        self.save_callback = save_callback

        self.title(f"Edit Configuration: {config_name}")
        self.geometry("500x600")
        self.resizable(False, False)
        self._create_widgets()
        self._populate_fields()

        self.protocol("WM_DELETE_WINDOW", self.on_close)
        self.transient(root)
        self.grab_set()

    def _create_widgets(self):
        self.fields = {}

        for idx, (key, value) in enumerate(self.config_data.items()):
            if key == "open_steps":
                continue

            label = ttk.Label(self, text=key)
            label.grid(row=idx, column=0, sticky=tk.W, padx=10, pady=5)

            if CONFIG_SCHEMA[key] == bool:
                var = tk.BooleanVar(value=value)
                entry = ttk.Checkbutton(self, variable=var)
            else:
                var = tk.StringVar(value=str(value))
                entry = ttk.Entry(self, textvariable=var, width=30)

            entry.grid(row=idx, column=1, padx=10, pady=5)
            self.fields[key] = var

        self.open_steps_button = ttk.Button(self, text="Edit Open Steps", command=self.edit_open_steps)
        self.open_steps_button.grid(row=idx + 1, column=0, columnspan=2, pady=10)

        self.save_button = ttk.Button(self, text="Save", command=self.save)
        self.save_button.grid(row=idx + 2, column=0, columnspan=2, pady=10)

        self.config_name_var = tk.StringVar(value=self.original_config_name)
        self.config_name_entry = ttk.Entry(self, textvariable=self.config_name_var, width=30)
        self.config_name_entry.grid(row=idx + 3, column=1, padx=10, pady=5)
        self.config_name_label = ttk.Label(self, text="Config Name")
        self.config_name_label.grid(row=idx + 3, column=0, sticky=tk.W, padx=10, pady=5)

    def _populate_fields(self):
        for key, value in self.config_data.items():
            if key in self.fields:
                self.fields[key].set(value)

    def edit_open_steps(self):
        EditOpenStepsWindow(self, self.config_name, self.config_data.get("open_steps", []), self.update_open_steps)

    def update_open_steps(self, open_steps):
        self.config_data["open_steps"] = open_steps

    def _convert_value(self, key, value):
        try:
            return CONFIG_SCHEMA[key](value.get())
        except ValueError:
            messagebox.showerror("Error", f"Invalid value for {key}. Expected {CONFIG_SCHEMA[key].__name__}.")
            return None

    def save(self):
        new_config = {}
        for key, var in self.fields.items():
            converted_value = self._convert_value(key, var)
            if converted_value is None:
                return
            new_config[key] = converted_value

        new_config["open_steps"] = self.config_data.get("open_steps", [])

        new_config_name = self.config_name_var.get()

        if new_config_name != self.original_config_name:
            if new_config_name in self.parent.config['applications']:
                messagebox.showerror("Error",
                                     f"Configuration name '{new_config_name}' already exists. Please choose a different name.")
                return

            # Remove the old configuration
            del self.parent.config['applications'][self.original_config_name]
            logger.info(f"Removed old configuration: {self.original_config_name}")

        # Add the new or updated configuration
        self.parent.config['applications'][new_config_name] = new_config
        logger.info(f"Added/Updated configuration: {new_config_name}")

        self.save_callback(new_config_name, new_config)
        self.on_close()

    def on_close(self):
        self.grab_release()
        self.parent.enable_main_window()
        self.destroy()