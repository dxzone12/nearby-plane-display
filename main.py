import argparse
import requests
import tkinter as tk
import tkinter.ttk as ttk
from DetailsDisplay import DetailsDisplay


def parse_args():
    parser = argparse.ArgumentParser(prog="Nearby Plane Display",
                                     description="Displays nearby planes based on given coordinates.")
    
    parser.add_argument("latitude", type=float, help="Latitude of the center point")
    parser.add_argument("longitude", type=float, help="Longitude of the center point")
    parser.add_argument("-H", "--hostname", type=str, default="localhost", help="Hostname of the readsb api endpoint (default: localhost)")
    parser.add_argument("-p", "--port", type=int, default=54321, help="Port of the readsb api endpoint (default: 54321)")
    parser.add_argument("-r", "--radius", type=int, default=150, help="Radius of the circle in kilometers (default: 150 nmi)")
    
    return parser.parse_args()

def main():
    args = parse_args()

    url = f"http://{args.hostname}:{args.port}/?circle={args.latitude},{args.longitude},{args.radius}&filter_with_pos"
    
    window = tk.Tk()
    window.title("Nearby Plane Display")
    # window.attributes("-fullscreen", True)
    
    window.columnconfigure(0, weight=1, minsize=100)
    window.columnconfigure(1, weight=2, minsize=100)
    window.rowconfigure(0, weight=1, minsize=100)

    left_frame = ttk.Frame(master=window)
    left_frame.grid(row=0, column=0, sticky="nsew")

    right_frame = ttk.Frame(master=window)
    right_frame.grid(row=0, column=1, sticky="nsew")

    details_frame = DetailsDisplay(right_frame)

    left_frame.columnconfigure(0, weight=1)
    left_frame.rowconfigure(0, weight=1)
    image_label = ttk.Label(master=left_frame, text="no image found", anchor=tk.CENTER, borderwidth=1, relief=tk.SUNKEN)
    image_label.grid(row=0, column=0, sticky="nsew")

    window.mainloop()

    # resp = requests.get(url)
    # response_json = resp.json()
    # print(response_json)


if __name__ == "__main__":
    main()
