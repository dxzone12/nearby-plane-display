import tkinter as tk
import tkinter.ttk as ttk
from PlaneDetails import PlaneDetails

class PlaneDetailsFrame:
    def __init__(self, parent: ttk.Frame):
        self.frame = parent
        self.frame.columnconfigure(0, weight=1)
        self.frame.columnconfigure(1, weight=1)
        for i in range(13):
            self.frame.rowconfigure(i, weight=1)
        
        # Initialise all the labels
        ttk.Label(master=self.frame, text="Callsign:", anchor=tk.W).grid(row=0, column=0, sticky=tk.NSEW, pady=2.5)
        ttk.Label(master=self.frame, text="Airline:", anchor=tk.W).grid(row=1, column=0, sticky=tk.NSEW, pady=2.5)
        ttk.Label(master=self.frame, text="Route:", anchor=tk.W).grid(row=2, column=0, sticky=tk.NSEW, pady=2.5)
        ttk.Label(master=self.frame, text="Model:", anchor=tk.W).grid(row=3, column=0, sticky=tk.NSEW, pady=2.5)
        ttk.Label(master=self.frame, text="Model Long:", anchor=tk.W).grid(row=4, column=0, sticky=tk.NSEW, pady=2.5)
        ttk.Label(master=self.frame, text="Squawk:", anchor=tk.W).grid(row=5, column=0, sticky=tk.NSEW, pady=2.5)
        ttk.Label(master=self.frame, text="Registration:", anchor=tk.W).grid(row=6, column=0, sticky=tk.NSEW, pady=2.5)
        ttk.Label(master=self.frame, text="Altitude:", anchor=tk.W).grid(row=7, column=0, sticky=tk.NSEW, pady=2.5)
        ttk.Label(master=self.frame, text="Altitude Rate:", anchor=tk.W).grid(row=8, column=0, sticky=tk.NSEW, pady=2.5)
        ttk.Label(master=self.frame, text="Ground Speed:", anchor=tk.W).grid(row=9, column=0, sticky=tk.NSEW, pady=2.5)
        ttk.Label(master=self.frame, text="Distance From Center:", anchor=tk.W).grid(row=10, column=0, sticky=tk.NSEW, pady=2.5)
        ttk.Label(master=self.frame, text="Position Received Ago:", anchor=tk.W).grid(row=11, column=0, sticky=tk.NSEW, pady=2.5)
        ttk.Label(master=self.frame, text="Plane Seen Ago:", anchor=tk.W).grid(row=12, column=0, sticky=tk.NSEW, pady=2.5)

        self._callsign_label = ttk.Label(master=self.frame, text="", anchor=tk.W)
        self._callsign_label.grid(row=0, column=1, sticky=tk.NSEW, padx=5)
        self._airline_label = ttk.Label(master=self.frame, text="", anchor=tk.W)
        self._airline_label.grid(row=1, column=1, sticky=tk.NSEW, padx=5)
        self._route_label = ttk.Label(master=self.frame, text="", anchor=tk.W)
        self._route_label.grid(row=2, column=1, sticky=tk.NSEW, padx=5)
        self._Model_label = ttk.Label(master=self.frame, text="", anchor=tk.W)
        self._Model_label.grid(row=3, column=1, sticky=tk.NSEW, padx=5)
        self._model_long_label = ttk.Label(master=self.frame, text="", anchor=tk.W)
        self._model_long_label.grid(row=4, column=1, sticky=tk.NSEW, padx=5)
        self._squawk_label = ttk.Label(master=self.frame, text="", anchor=tk.W)
        self._squawk_label.grid(row=5, column=1, sticky=tk.NSEW, padx=5)
        self._rego_label = ttk.Label(master=self.frame, text="", anchor=tk.W)
        self._rego_label.grid(row=6, column=1, sticky=tk.NSEW, padx=5)
        self._alt_label = ttk.Label(master=self.frame, text="", anchor=tk.W)
        self._alt_label.grid(row=7, column=1, sticky=tk.NSEW, padx=5)
        self._alt_rate_label = ttk.Label(master=self.frame, text="", anchor=tk.W)
        self._alt_rate_label.grid(row=8, column=1, sticky=tk.NSEW, padx=5)
        self._ground_speed_label = ttk.Label(master=self.frame, text="", anchor=tk.W)
        self._ground_speed_label.grid(row=9, column=1, sticky=tk.NSEW, padx=5)
        self._distance_from_center_label = ttk.Label(master=self.frame, text="", anchor=tk.W)
        self._distance_from_center_label.grid(row=10, column=1, sticky=tk.NSEW, padx=5)
        self._position_received_ago_label = ttk.Label(master=self.frame, text="", anchor=tk.W)
        self._position_received_ago_label.grid(row=11, column=1, sticky=tk.NSEW, padx=5)
        self._plane_seen_ago_label = ttk.Label(master=self.frame, text="", anchor=tk.W)
        self._plane_seen_ago_label.grid(row=12, column=1, sticky=tk.NSEW, padx=5)

    def update_details(self, plane_details: PlaneDetails | None):
        if plane_details is None:
            self._callsign_label["text"] = "No planes found in the specified area."
            return
        
        self._callsign_label["text"] = plane_details.call_sign
        self._airline_label["text"] = plane_details.airline
        self._route_label["text"] = "Not Supported Yet"
        self._Model_label["text"] = plane_details.model
        self._model_long_label["text"] = plane_details.model_long
        self._squawk_label["text"] = plane_details.squawk
        self._rego_label["text"] = plane_details.registration
        self._alt_label["text"] = f"{plane_details.altitude} ft"
        self._alt_rate_label["text"] = f"{plane_details.altitude_rate} ft/min"
        self._ground_speed_label["text"] = f"{plane_details.ground_speed} kt"
        self._distance_from_center_label["text"] = f"{plane_details.distance_from_center} nm"
        self._position_received_ago_label["text"] = f"{plane_details.pos_received_ago} sec"
        self._plane_seen_ago_label["text"] = f"{plane_details.plane_seen_ago} sec"
