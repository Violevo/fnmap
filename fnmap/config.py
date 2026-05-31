from dataclasses import dataclass
from pathlib import Path

PATCH = "40.40"
BASE_TILE_URL = "https://fortnite.gg/maps"
TILE_SIZE = 256
MIN_ZOOM = 0
MAX_ZOOM = 7

BACKGROUND_COLOR = (47, 49, 55)
BACKGROUND_TOLERANCE = 3

ROOT_DIR = Path(__file__).resolve().parents[1]
DEFAULT_CACHE_DIR = ROOT_DIR / "cache" / "tiles"
DEFAULT_OUTPUT_DIR = ROOT_DIR / "output" / "maps"

# Bounds used by fortnite.gg for the main Battle Royale island.
MAP_LEFT = 29.71
MAP_TOP = 36.02
MAP_RIGHT = 213.37
MAP_BOTTOM = 230.53


@dataclass(frozen=True)
class TileArea:
    zoom: int
    x_start: int
    x_end: int
    y_start: int
    y_end: int

    @property
    def tile_width(self):
        return self.x_end - self.x_start

    @property
    def tile_height(self):
        return self.y_end - self.y_start

    @property
    def pixel_width(self):
        return self.tile_width * TILE_SIZE

    @property
    def pixel_height(self):
        return self.tile_height * TILE_SIZE

    def iter_tiles(self):
        for y in range(self.y_start, self.y_end):
            for x in range(self.x_start, self.x_end):
                yield x, y


def resolution_for_zoom(zoom):
    return TILE_SIZE * (2**zoom)


def validate_zoom(zoom):
    if zoom < MIN_ZOOM or zoom > MAX_ZOOM:
        raise ValueError(f"zoom level must be between {MIN_ZOOM} and {MAX_ZOOM}")


def full_tile_area(zoom):
    validate_zoom(zoom)
    tile_count = 2**zoom
    return TileArea(zoom=zoom, x_start=0, x_end=tile_count, y_start=0, y_end=tile_count)


def map_tile_area(zoom):
    validate_zoom(zoom)
    scale = 2**zoom
    full_area = full_tile_area(zoom)

    x_start = int(MAP_LEFT * scale) // TILE_SIZE
    y_start = int(MAP_TOP * scale) // TILE_SIZE
    x_end = (round(MAP_RIGHT * scale) + TILE_SIZE - 1) // TILE_SIZE
    y_end = (round(MAP_BOTTOM * scale) + TILE_SIZE - 1) // TILE_SIZE

    return TileArea(
        zoom=zoom,
        x_start=max(full_area.x_start, x_start),
        x_end=min(full_area.x_end, x_end),
        y_start=max(full_area.y_start, y_start),
        y_end=min(full_area.y_end, y_end),
    )
