from typing import NamedTuple

class PlaneDetails(NamedTuple):
    call_sign: str
    squawk: str
    registration: str
    model: str
    model_long: str
    airline: str
    altitude: int
    altitude_rate: int
    ground_speed: float
    distance_from_center: float
    pos_received_ago: int
    plane_seen_ago: int
