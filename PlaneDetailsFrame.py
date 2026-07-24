import tkinter as tk
import tkinter.ttk as ttk
from PlaneDetails import PlaneDetails
from PIL import Image, ImageTk

class PlaneDetailsFrame:
    def __init__(self, title_frame: ttk.Frame, bottom_frame: ttk.Frame, image_frame: ttk.Frame):
        self._title_frame = title_frame
        self._title_frame.columnconfigure(0, weight=1)
        self._title_frame.columnconfigure(1, weight=1)
        for i in range(4):
            self._title_frame.rowconfigure(i, weight=1)
        
        self._bottom_frame = bottom_frame
        self._bottom_frame.columnconfigure(0, weight=1)
        self._bottom_frame.columnconfigure(1, weight=1)
        self._bottom_frame.columnconfigure(2, weight=1)
        self._bottom_frame.columnconfigure(3, weight=1)
        for i in range(4):
            self._bottom_frame.rowconfigure(i, weight=1)
        
        # Initialise image frame
        self._image_frame = image_frame
        self._image_label = ttk.Label(master=self._image_frame, text="no image found", anchor=tk.CENTER, borderwidth=1, relief=tk.SUNKEN)
        self._image_label.grid(row=0, column=0, sticky=tk.NSEW)
        self._image_file_name = ""
        self._resized_image: ImageTk.PhotoImage | None = None

        # Initialise title frame
        ttk.Label(master=self._title_frame, text="Callsign:", anchor=tk.W).grid(row=0, column=0, sticky=tk.NSEW, padx=3)
        ttk.Label(master=self._title_frame, text="Airline:", anchor=tk.W).grid(row=1, column=0, sticky=tk.NSEW, padx=3)
        ttk.Label(master=self._title_frame, text="Route:", anchor=tk.W).grid(row=2, column=0, sticky=tk.NSEW, padx=3)
        ttk.Label(master=self._title_frame, text="Model:", anchor=tk.W).grid(row=3, column=0, sticky=tk.NSEW, padx=3)

        self._callsign_label = ttk.Label(master=self._title_frame, text="", anchor=tk.W)
        self._callsign_label.grid(row=0, column=1, sticky=tk.NSEW, padx=5)
        self._airline_label = ttk.Label(master=self._title_frame, text="", anchor=tk.W)
        self._airline_label.grid(row=1, column=1, sticky=tk.NSEW, padx=5)
        self._route_label = ttk.Label(master=self._title_frame, text="", anchor=tk.W)
        self._route_label.grid(row=2, column=1, sticky=tk.NSEW, padx=5)
        self._Model_label = ttk.Label(master=self._title_frame, text="", anchor=tk.W)
        self._Model_label.grid(row=3, column=1, sticky=tk.NSEW, padx=5)

        # Initialise bottom frame
        ttk.Label(master=self._bottom_frame, text="Altitude:", anchor=tk.W).grid(row=0, column=0, sticky=tk.NSEW)
        ttk.Label(master=self._bottom_frame, text="Ground Speed:", anchor=tk.W).grid(row=1, column=0, sticky=tk.NSEW)
        ttk.Label(master=self._bottom_frame, text="Distance:", anchor=tk.W).grid(row=2, column=0, sticky=tk.NSEW)

        ttk.Label(master=self._bottom_frame, text="Squawk:", anchor=tk.W).grid(row=0, column=2, sticky=tk.NSEW)
        ttk.Label(master=self._bottom_frame, text="Registration:", anchor=tk.W).grid(row=1, column=2, sticky=tk.NSEW)
        ttk.Label(master=self._bottom_frame, text="Last seen:", anchor=tk.W).grid(row=2, column=2, sticky=tk.NSEW)

        self._alt_label = ttk.Label(master=self._bottom_frame, text="", anchor=tk.W)
        self._alt_label.grid(row=0, column=1, sticky=tk.NSEW, padx=5)
        self._ground_speed_label = ttk.Label(master=self._bottom_frame, text="", anchor=tk.W)
        self._ground_speed_label.grid(row=1, column=1, sticky=tk.NSEW, padx=5)
        self._distance_from_center_label = ttk.Label(master=self._bottom_frame, text="", anchor=tk.W)
        self._distance_from_center_label.grid(row=2, column=1, sticky=tk.NSEW, padx=5)

        self._squawk_label = ttk.Label(master=self._bottom_frame, text="", anchor=tk.W)
        self._squawk_label.grid(row=0, column=3, sticky=tk.NSEW, padx=5)
        self._rego_label = ttk.Label(master=self._bottom_frame, text="", anchor=tk.W)
        self._rego_label.grid(row=1, column=3, sticky=tk.NSEW, padx=5)
        self._last_seen_label = ttk.Label(master=self._bottom_frame, text="", anchor=tk.W)
        self._last_seen_label.grid(row=2, column=3, sticky=tk.NSEW, padx=5)

    def empty_details(self):
        self._callsign_label["text"] = "No planes found in the specified area."
        self._airline_label["text"] = ""
        self._route_label["text"] = ""
        self._Model_label["text"] = ""
        self._squawk_label["text"] = ""
        self._rego_label["text"] = ""
        self._alt_label["text"] = ""
        self._ground_speed_label["text"] = ""
        self._distance_from_center_label["text"] = ""
        self._last_seen_label["text"] = ""

    def update_details(self, plane_details: PlaneDetails | None):
        if plane_details is None:
            self.empty_details()
            return

        self._callsign_label["text"] = plane_details.call_sign
        self._airline_label["text"] = plane_details.airline
        self._route_label["text"] = plane_details.route
        self._Model_label["text"] = f"{plane_details.model_long} ({plane_details.model})"
        self._squawk_label["text"] = plane_details.squawk
        self._rego_label["text"] = plane_details.registration
        self._alt_label["text"] = f"{plane_details.altitude} ft{self.altitude_change_indicator(plane_details.altitude_rate)}"
        self._ground_speed_label["text"] = f"{plane_details.ground_speed} kt"
        self._distance_from_center_label["text"] = f"{plane_details.distance_from_center} nm"
        self._last_seen_label["text"] = f"{plane_details.plane_seen_ago} sec (pos: {plane_details.pos_received_ago} sec)"

        image_to_set = self.get_image(plane_details.image_file_name)
        self._image_label.config(image=image_to_set)

    def get_image(self, file_name: str) -> ImageTk.PhotoImage | str:
        if file_name == "":
            self._image_file_name = ""
            self._resized_image = None
            return ""
        
        if file_name == self._image_file_name:
            return self._resized_image if self._resized_image is not None else ""
        
        raw_image = Image.open(file_name)
        self._resized_image = ImageTk.PhotoImage(raw_image)

        self._image_file_name = file_name
        return self._resized_image

    def altitude_change_indicator(self, altitude_rate: int) -> str:
        if altitude_rate > 0:
            return " (▲)"
        elif altitude_rate < 0:
            return " (▼)"
        else:
            return ""