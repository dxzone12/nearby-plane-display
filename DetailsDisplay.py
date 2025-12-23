import tkinter.ttk as ttk

class DetailsDisplay:
    def __init__(self, parent_frame: ttk.Frame):
        self.parent_frame = parent_frame

        # set parent frame properties
        self.parent_frame.columnconfigure(0, weight=1, minsize=100)

        self.url_label = ttk.Label(master=self.parent_frame, text="Details Display")
        self.url_label.grid(row=0, column=0, sticky="n")
