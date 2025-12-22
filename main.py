
import argparse
import requests


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
    
    resp = requests.get(url)
    print(resp.json())


if __name__ == "__main__":
    main()
