import argparse
from pathlib import Path
import requests
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont
from PlaneDetails import PlaneDetails
from PlaneDetailsFrame import PlaneDetailsFrame
import re

current_plane_deets: PlaneDetails | None = None
window: tk.Tk  = tk.Tk()

standing_data_base_dir: Path

airline_lookup_cache: dict[str, str | None] = {}

def parse_args():
    parser = argparse.ArgumentParser(prog="Nearby Plane Display",
                                     description="Displays nearby planes based on given coordinates.")

    parser.add_argument("latitude", type=float, help="Latitude of the center point")
    parser.add_argument("longitude", type=float, help="Longitude of the center point")
    parser.add_argument("-H", "--hostname", type=str, default="localhost", help="Hostname of the readsb api endpoint (default: localhost)")
    parser.add_argument("-p", "--port", type=int, default=54321, help="Port of the readsb api endpoint (default: 54321)")
    parser.add_argument("-r", "--radius", type=int, default=150, help="Radius of the circle in kilometers (default: 150 nmi)")
    parser.add_argument("-d", "--data_dir", type=str, default="/usr/local/share/npd/standing-data-main", help="Path to standing data directory")

    return parser.parse_args()

def normalise_callsign(callsign: str) -> tuple[str, str] | None:
    callsign = callsign.strip()
    match = re.match(r"^(?P<code>[A-Z]{2,3}|[A-Z][0-9]|[0-9][A-Z])(?P<number>\d[A-Z0-9]*)", callsign)
    if match:
        code = match.group("code")
        number = match.group("number").lstrip("0")
        if not number or number.isalpha():
            number = "0" + number
        return (code, number)
    return None

def lookup_airline_local_db(normalised_callsign: tuple[str, str], airline: str | None) -> str | None:
    airline_code = normalised_callsign[0]

    if airline_code in airline_lookup_cache:
        return airline_lookup_cache[airline_code]

    looked_up_airline = None
    airline_csv = standing_data_base_dir / "airlines" / "schema-01" / "airlines.csv"
    if airline_csv.exists() and airline_csv.is_file():
        with airline_csv.open() as f:
            for line in f:
                line_parts = line.split(",")
                if len(line_parts) < 2:
                    continue
                if line_parts[0].strip() == airline_code:
                    looked_up_airline = line_parts[1].strip()
                    break
    
    # Now that we have the given airline and the looked up one we cache and use the shortest
    looked_up_length = len(looked_up_airline) if looked_up_airline is not None else 10_000
    passed_in_length = len(airline) if airline is not None else 10_000

    best_option = looked_up_airline if looked_up_length < passed_in_length else airline
    airline_lookup_cache[airline_code] = best_option
    return best_option

def lookup_route_local_db(normalised_callsign: tuple[str, str]) -> str | None:
    pass

def get_closest_plain_deets(plane_data_json: dict) -> PlaneDetails | None:
    if not isinstance(plane_data_json, dict):
        raise TypeError("Input must be a dictionary representing plane data in JSON format.")

    if plane_data_json["resultCount"] < 1:
        return None

    closest_plane = min(plane_data_json["aircraft"], key=lambda x: x["dst"])

    if not isinstance(closest_plane, dict):
        raise TypeError("Each plane entry must be a dictionary.")
    
    callsign = closest_plane.get("flight", None)
    airline = closest_plane.get("ownOp", None)

    normalised_callsign = normalise_callsign(callsign) if callsign is not None else None

    route = lookup_route_local_db(normalised_callsign) if normalised_callsign is not None else None

    # Attempt to resolve airline if it wasn't supplied
    if normalised_callsign is not None:
        airline = lookup_airline_local_db(normalised_callsign, airline)
    if airline is None:
        airline = "Unknown"

    if callsign is None:
        callsign = "Unknown"

    return PlaneDetails(
        call_sign=callsign,
        squawk=closest_plane.get("squawk", "Unknown"),
        registration=closest_plane.get("r", "Unknown"),
        model=closest_plane.get("t", "Unknown"),
        model_long=closest_plane.get("desc", "Unknown"),
        airline=airline,
        altitude=closest_plane.get("alt_baro", 0),
        altitude_rate=closest_plane.get("baro_rate", 0),
        ground_speed=closest_plane.get("gs", 0.0),
        distance_from_center=closest_plane["dst"],
        pos_received_ago=closest_plane["seen_pos"],
        plane_seen_ago=closest_plane["seen"],
        route=route if route is not None else "Not Supported Yet"
    )

def get_and_update_plane_details(url: str, frame: PlaneDetailsFrame) -> PlaneDetails | None:
    resp = requests.get(url)
    response_json = resp.json()
    current_plane_deets = get_closest_plain_deets(response_json)
    frame.update_details(current_plane_deets)
    window.after(1000, get_and_update_plane_details, url, frame)

def main():
    args = parse_args()
    global standing_data_base_dir
    standing_data_base_dir= Path(args.data_dir)

    url = f"http://{args.hostname}:{args.port}/?circle={args.latitude},{args.longitude},{args.radius}&filter_with_pos"

    window.title("Nearby Plane Display")
    # window.geometry("800x480")
    window.attributes("-fullscreen", True)

    window.columnconfigure(0, weight=1, minsize=200)
    window.columnconfigure(1, weight=1, minsize=100)
    window.rowconfigure(0, weight=2, minsize=100)
    window.rowconfigure(1, weight=1, minsize=100)

    left_frame = ttk.Frame(master=window)
    left_frame.grid(row=0, column=0, sticky=tk.NSEW)

    left_frame.columnconfigure(0, weight=1)
    left_frame.rowconfigure(0, weight=1)
    image_label = ttk.Label(master=left_frame, text="no image found", anchor=tk.CENTER, borderwidth=1, relief=tk.SUNKEN)
    image_label.grid(row=0, column=0, sticky=tk.NSEW)

    right_frame = ttk.Frame(master=window)
    right_frame.grid(row=0, column=1, sticky=tk.NSEW)

    bottom_frame = ttk.Frame(master=window)
    bottom_frame.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)
    
    details_frame = PlaneDetailsFrame(right_frame, bottom_frame)

    style = ttk.Style(window)
    style.configure("TLabel", font=("helvetica", 20))

    window.after(0, get_and_update_plane_details, url, details_frame)

    window.bind("<Escape>", lambda e: window.destroy())
    window.mainloop()

if __name__ == "__main__":
    main()
