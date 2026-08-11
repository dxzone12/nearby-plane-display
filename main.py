import argparse
from pathlib import Path
from typing import cast
import requests
import tkinter as tk
import tkinter.ttk as ttk
import tkinter.font as tkfont
from PlaneDetails import PlaneDetails
from PlaneDetailsFrame import PlaneDetailsFrame
import re
from datetime import datetime
import tempfile
import os

current_plane_deets: PlaneDetails | None = None
window: tk.Tk  = tk.Tk()

standing_data_base_dir: Path

airline_lookup_cache: dict[str, str | None] = {}
airport_lookup_cache: dict[str, str] = {}

photo_lookup_cache: dict[str, tuple[str | None, str | None, datetime]] = {}
photo_cache_dir = tempfile.TemporaryDirectory(prefix="nearby-plane-display-")

email_address: str

def parse_args():
    parser = argparse.ArgumentParser(prog="Nearby Plane Display",
                                     description="Displays nearby planes based on given coordinates.")

    parser.add_argument("latitude", type=float, help="Latitude of the center point")
    parser.add_argument("longitude", type=float, help="Longitude of the center point")
    parser.add_argument("-H", "--hostname", type=str, default="localhost", help="Hostname of the readsb api endpoint (default: localhost)")
    parser.add_argument("-p", "--port", type=int, default=54321, help="Port of the readsb api endpoint (default: 54321)")
    parser.add_argument("-r", "--radius", type=int, default=150, help="Radius of the circle in kilometers (default: 150 nmi)")
    parser.add_argument("-d", "--data_dir", type=str, default="/usr/local/share/npd/standing-data-main", help="Path to standing data directory")
    parser.add_argument("-e", "--email", type=str, required=True, help="Email address to use in the planespotters API User-Agent header")

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
    code_component = normalised_callsign[0]
    number_component = normalised_callsign[1]

    route_dir = standing_data_base_dir / "routes" / "schema-01" / code_component[0]

    route = None

    all_csv = route_dir / f"{code_component}-all.csv"
    if all_csv.exists() and all_csv.is_file():
        route =read_route_from_csv(all_csv, f"{code_component}{number_component}")

    numbered_csv = route_dir / f"{code_component}-{number_component[0]}.csv"
    if numbered_csv.exists() and numbered_csv.is_file():
        route = read_route_from_csv(numbered_csv, f"{code_component}{number_component}")

    if route is not None:
        airport_codes = [get_best_airport_code(x) for x in route.split("-")]
        route = "-".join(airport_codes)

    return route

def read_route_from_csv(file_path: Path, normalised_callsign: str) -> str | None:
    with file_path.open() as f:
        for line in f:
            line_parts = line.split(",")
            if len(line_parts) < 5:
                continue
            if line_parts[0].strip() == normalised_callsign:
                return line_parts[4].strip()
    return None

def get_best_airport_code(airport_code: str) -> str:
    airport_csv = standing_data_base_dir / "airports" / "schema-01" / airport_code[0] / f"{airport_code[0:2]}.csv"

    if airport_code in airport_lookup_cache:
        return airport_lookup_cache[airport_code]
    
    best_code = airport_code
    with airport_csv.open() as f:
        for line in f:
            line_parts = line.split(",")
            if len(line_parts) < 4:
                continue
            if line_parts[0].strip() == airport_code:
                iata_code = line_parts[3].strip()
                if iata_code:
                    best_code = iata_code
                break
    
    airport_lookup_cache[airport_code] = best_code
    return best_code

def download_photo(url: str) -> str | None:
    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            delete_on_close=False,
            dir=photo_cache_dir.name,
            prefix="photo-",
            suffix=".jpg",
        )
        with open(temp_file.name, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return temp_file.name
    except Exception as e:
        print(f"Error downloading photo from {url}: {e}")
        return None

def get_photo_for_registration(registration: str | None) -> tuple[str | None, str | None]:
    if (registration is None):
        return (None, None)
    
    # Check if we have it cached
    if registration in photo_lookup_cache:
        cached_photo_file_name, cached_photo_credit, cached_timestamp = photo_lookup_cache[registration]
        # Check if the cached entry is older than 24 hours
        if (datetime.now() - cached_timestamp).total_seconds() < 24 * 3600:
            return (cached_photo_file_name, cached_photo_credit)
        else:
            # Remove stale cache entry
            (removed_cache_path, _, _) = photo_lookup_cache.pop(registration)
            # Cleanup the temp file
            if removed_cache_path is not None and os.path.exists(removed_cache_path):
                os.remove(removed_cache_path)

    # If not cached or cache is stale, fetch from the API
    lookup_url = f"https://api.planespotters.net/pub/photos/reg/{registration}"
    headers = {
        "User-Agent": f"Nearby Plane Display ({email_address})"
    }
    resp = requests.get(lookup_url, headers=headers)
    resp_json = cast(dict, resp.json())

    if ("error" in resp_json):
        print(f"Error from planespotters API: {resp_json['error']}")
        photo_lookup_cache[registration] = (None, None, datetime.now())
        return (None, None)

    photos = resp_json.get("photos", [])
    recent_photo = photos[0] if photos else None

    if recent_photo is None:
        print(f"No photos found for registration {registration}")
        photo_lookup_cache[registration] = (None, None, datetime.now())
        return (None, None)
    
    credit = recent_photo.get("photographer", None)
    thumbnail_url = recent_photo.get("thumbnail", {}).get("src", None)
    large_thumbnail_url = recent_photo.get("thumbnail_large", {}).get("src", None)
    resolved_url = large_thumbnail_url or thumbnail_url or None

    downloaded_photo_path = download_photo(resolved_url) if resolved_url else None

    photo_lookup_cache[registration] = (downloaded_photo_path, credit, datetime.now())
    print(f"Fetched photo for registration {registration}: URL={resolved_url}, Credit={credit}, WrittenTo={downloaded_photo_path}")
    return (downloaded_photo_path, credit)

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
    
    registration = closest_plane.get("r", None)
    image_file_name, image_credit = get_photo_for_registration(registration)

    return PlaneDetails(
        call_sign=callsign if callsign is not None else "Unknown",
        squawk=closest_plane.get("squawk", "Unknown"),
        registration=registration if registration is not None else "Unknown",
        model=closest_plane.get("t", "Unknown"),
        model_long=closest_plane.get("desc", "Unknown"),
        airline=airline if airline is not None else "Unknown",
        altitude=closest_plane.get("alt_baro", 0),
        altitude_rate=closest_plane.get("baro_rate", 0),
        ground_speed=closest_plane.get("gs", 0.0),
        distance_from_center=closest_plane["dst"],
        pos_received_ago=closest_plane["seen_pos"],
        plane_seen_ago=closest_plane["seen"],
        route=route if route is not None else "Not Supported Yet",
        image_file_name=image_file_name if image_file_name is not None else "",
        image_credit=f"{image_credit} via planespotters.net" if image_credit is not None else ""
    )

def get_and_update_plane_details(url: str, frame: PlaneDetailsFrame) -> PlaneDetails | None:
    try:
        resp = requests.get(url)
        response_json = resp.json()
        current_plane_deets = get_closest_plain_deets(response_json)
        frame.update_details(current_plane_deets)
    except Exception as e:
        print(f"Error occurred: {e}")
    finally:
        window.after(1000, get_and_update_plane_details, url, frame)

def main():
    args = parse_args()
    
    global standing_data_base_dir
    standing_data_base_dir= Path(args.data_dir)
    global email_address
    email_address = args.email

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

    right_frame = ttk.Frame(master=window)
    right_frame.grid(row=0, column=1, sticky=tk.NSEW)

    bottom_frame = ttk.Frame(master=window)
    bottom_frame.grid(row=1, column=0, columnspan=2, sticky=tk.NSEW)
    
    details_frame = PlaneDetailsFrame(right_frame, bottom_frame, left_frame)

    style = ttk.Style(window)
    style.configure("TLabel", font=("helvetica", 20))

    window.after(0, get_and_update_plane_details, url, details_frame)

    window.bind("<Escape>", lambda e: window.destroy())
    window.mainloop()

if __name__ == "__main__":
    main()
