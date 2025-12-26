import argparse
import requests
import tkinter as tk
import tkinter.ttk as ttk
from PlaneDetails import PlaneDetails
from PlaneDetailsFrame import PlaneDetailsFrame

def parse_args():
    parser = argparse.ArgumentParser(prog="Nearby Plane Display",
                                     description="Displays nearby planes based on given coordinates.")
    
    parser.add_argument("latitude", type=float, help="Latitude of the center point")
    parser.add_argument("longitude", type=float, help="Longitude of the center point")
    parser.add_argument("-H", "--hostname", type=str, default="localhost", help="Hostname of the readsb api endpoint (default: localhost)")
    parser.add_argument("-p", "--port", type=int, default=54321, help="Port of the readsb api endpoint (default: 54321)")
    parser.add_argument("-r", "--radius", type=int, default=150, help="Radius of the circle in kilometers (default: 150 nmi)")
    
    return parser.parse_args()

def get_closest_plain_deets(plane_data_json: dict) -> PlaneDetails | None:
    print(plane_data_json)
    if not isinstance(plane_data_json, dict):
        raise TypeError("Input must be a dictionary representing plane data in JSON format.")
    
    if plane_data_json["resultCount"] < 1:
        return None
    
    closest_plane = min(plane_data_json["aircraft"], key=lambda x: x["dst"])

    if not isinstance(closest_plane, dict):
        raise TypeError("Each plane entry must be a dictionary.")

    return PlaneDetails(
        call_sign=closest_plane.get("flight", "Unknown"),
        squawk=closest_plane.get("squawk", "Unknown"),
        registration=closest_plane.get("r", "Unknown"),
        model=closest_plane.get("t", "Unknown"),
        model_long=closest_plane.get("desc", "Unknown"),
        airline=closest_plane.get("ownOp", "Unknown"),
        altitude=closest_plane.get("alt_baro", 0),
        altitude_rate=closest_plane.get("baro_rate", 0),
        ground_speed=closest_plane.get("gs", 0.0),
        distance_from_center=closest_plane["dst"],
        pos_received_ago=closest_plane["seen_pos"],
        plane_seen_ago=closest_plane["seen"]
    )

def main():
    args = parse_args()

    url = f"http://{args.hostname}:{args.port}/?circle={args.latitude},{args.longitude},{args.radius}&filter_with_pos"
    
    resp = requests.get(url)
    response_json = resp.json()
    plane_deets = get_closest_plain_deets(response_json)
    print(plane_deets)

    window = tk.Tk()
    window.title("Nearby Plane Display")
    # window.attributes("-fullscreen", True)
    
    window.columnconfigure(0, weight=1, minsize=100)
    window.columnconfigure(1, weight=2, minsize=100)
    window.rowconfigure(0, weight=1, minsize=100)

    left_frame = ttk.Frame(master=window)
    left_frame.grid(row=0, column=0, sticky=tk.NSEW)

    left_frame.columnconfigure(0, weight=1)
    left_frame.rowconfigure(0, weight=1)
    image_label = ttk.Label(master=left_frame, text="no image found", anchor=tk.CENTER, borderwidth=1, relief=tk.SUNKEN)
    image_label.grid(row=0, column=0, sticky=tk.NSEW)

    right_frame = ttk.Frame(master=window)
    right_frame.grid(row=0, column=1, sticky=tk.NSEW)
    details_frame = PlaneDetailsFrame(right_frame)

    details_frame.update_details(plane_deets)

    window.bind("<Escape>", lambda e: window.destroy())
    window.mainloop()

if __name__ == "__main__":
    main()
