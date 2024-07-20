import tkinter as tk
from data_transfer_gui import DataTransferGUI
import logging

# Set up logging
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(filename)s:%(funcName)s - %(message)s')
logger = logging.getLogger(__name__)

def main():
    """
    Main function to initialize and run the Data Transfer GUI application.
    """
    root = tk.Tk()
    app = DataTransferGUI(root)
    logger.info("Starting Data Transfer GUI application")
    root.mainloop()

if __name__ == "__main__":
    main()


