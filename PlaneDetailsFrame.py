import tkinter.ttk as ttk
from PlaneDetails import PlaneDetails

class PlaneDetailsFrame:
    def __init__(self, parent: ttk.Frame):
        self.frame = parent
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        for i in range(12):
            self.frame.rowconfigure(i, weight=1)
