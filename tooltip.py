import tkinter as tk

class ToolTip:
    """
    A class to create and manage tooltips for Tkinter widgets.
    """

    def __init__(self, widget, text):
        """
        Initialize the ToolTip class.

        Args:
            widget (tk.Widget): The widget to attach the tooltip to.
            text (str): The text to display in the tooltip.
        """
        self.widget = widget
        self.text = text
        self.tooltip = None
        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        """
        Show the tooltip.

        Args:
            event (tk.Event, optional): The event that triggered the tooltip. Defaults to None.
        """
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25
        self.tooltip = tk.Toplevel(self.widget)
        self.tooltip.wm_overrideredirect(True)
        self.tooltip.wm_geometry(f"+{x}+{y}")
        label = tk.Label(self.tooltip, text=self.text, justify=tk.LEFT,
                         background="#ffffe0", relief=tk.SOLID, borderwidth=1,
                         font=("tahoma", "10", "normal"))
        label.pack(ipadx=1)

    def hide_tooltip(self, event=None):
        """
        Hide the tooltip.

        Args:
            event (tk.Event, optional): The event that triggered the tooltip. Defaults to None.
        """
        if self.tooltip:
            self.tooltip.destroy()
            self.tooltip = None