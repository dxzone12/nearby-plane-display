import tkinter as tk
import tkinter.ttk as ttk
from PlaneDetails import PlaneDetails

class PlaneDetailsFrame:
    def __init__(self, parent: ttk.Frame):
        self.frame = parent
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        for i in range(12):
            self.frame.rowconfigure(i, weight=1)
    
    def update_details(self, plane_details: PlaneDetails | None):
        if plane_details is not None:
            no_plane_label = ttk.Label(master=self.frame, text="No planes found in the specified area.", anchor=tk.CENTER)
            no_plane_label.grid(row=0, column=0, columnspan=2, sticky=tk.NSEW)
            return
