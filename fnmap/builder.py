from dataclasses import dataclass
from pathlib import Path
import shutil

import requests
from PIL import Image

from .config import (
    BASE_TILE_URL,
    DEFAULT_CACHE_DIR,
    DEFAULT_OUTPUT_DIR,
    PATCH,
    TILE_SIZE,
    full_tile_area,
    map_tile_area,
    resolution_for_zoom,
)
from .image_tools import blank_row, is_background_image, is_background_tile, write_streamed_png


@dataclass(frozen=True)
class BuildOptions:
    zoom: int
    include_blank_tiles: bool
    patch: str = PATCH
    cache_dir: Path = DEFAULT_CACHE_DIR
    output_dir: Path = DEFAULT_OUTPUT_DIR
    keep_tiles: bool = False


class FortniteMapBuilder:
    def __init__(self):
        self.session = requests.Session()

    def build(self, options):
        output_area = full_tile_area(options.zoom)
        download_area = output_area if options.include_blank_tiles else map_tile_area(options.zoom)
        tile_dir = self._tile_dir(options)
        output_path = self._output_path(options)

        self._download_tiles(options, download_area, tile_dir)
        self._write_map(options, output_area, tile_dir, output_path)

        if not options.keep_tiles:
            shutil.rmtree(tile_dir)

        return output_path

    def _download_tiles(self, options, area, tile_dir):
        tile_dir.mkdir(parents=True, exist_ok=True)
        total = area.tile_width * area.tile_height

        for index, (x, y) in enumerate(area.iter_tiles(), start=1):
            tile_path = self._tile_path(tile_dir, x, y)
            if tile_path.exists():
                print(f"{index}/{total} cached tile {x},{y}")
                continue

            tile_data = self._fetch_tile(options.patch, options.zoom, x, y)

            if is_background_tile(tile_data):
                print(f"{index}/{total} blank tile {x},{y}")
                continue

            tile_path.write_bytes(tile_data)
            print(f"{index}/{total} downloaded tile {x},{y}")

    def _write_map(self, options, area, tile_dir, output_path):
        width = resolution_for_zoom(options.zoom)
        height = resolution_for_zoom(options.zoom)
        print(f"building {width} x {height} PNG")

        write_streamed_png(
            output_path=output_path,
            width=width,
            height=height,
            row_images=self._iter_rows(options, area, tile_dir),
        )

    def _iter_rows(self, options, area, tile_dir):
        for y in range(area.y_start, area.y_end):
            row = blank_row(area.pixel_width, options.include_blank_tiles)

            for x in range(area.x_start, area.x_end):
                tile_path = self._tile_path(tile_dir, x, y)
                if not tile_path.exists():
                    continue

                with Image.open(tile_path) as tile_image:
                    if not options.include_blank_tiles and is_background_image(tile_image):
                        continue

                    row.paste(tile_image.convert("RGBA"), ((x - area.x_start) * TILE_SIZE, 0))

            print(f"merged row {y + 1}/{area.y_end}")
            yield row

    def _fetch_tile(self, patch, zoom, x, y):
        url = f"{BASE_TILE_URL}/{patch}/{zoom}/{x}/{y}.webp"
        response = self.session.get(url, timeout=30)
        response.raise_for_status()

        content_type = response.headers.get("content-type", "")
        if not content_type.startswith("image/"):
            raise RuntimeError(f"expected image from {url}, got {content_type}")

        return response.content

    def _tile_dir(self, options):
        patch_name = options.patch.replace(".", "_")
        return options.cache_dir / f"patch_{patch_name}" / f"zoom_{options.zoom}"

    def _tile_path(self, tile_dir, x, y):
        return tile_dir / f"tile_{x}_{y}.webp"

    def _output_path(self, options):
        patch_name = options.patch.replace(".", "_")
        resolution = resolution_for_zoom(options.zoom)
        blank_mode = "with_blanks" if options.include_blank_tiles else "transparent_blanks"
        filename = f"fortnite_map_{patch_name}_z{options.zoom}_{resolution}_{blank_mode}.png"
        return options.output_dir / filename
