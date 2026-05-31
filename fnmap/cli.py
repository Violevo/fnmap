import argparse
from pathlib import Path

from .builder import BuildOptions, FortniteMapBuilder
from .config import MAX_ZOOM, MIN_ZOOM, PATCH, resolution_for_zoom


def main(argv=None):
    args = parse_args(argv)

    print("Fortnite map builder")
    print(f"Patch: {args.patch}")
    print()

    zoom = args.zoom if args.zoom is not None else ask_zoom()
    include_blank_tiles = resolve_blank_tile_mode(args)

    options = BuildOptions(
        zoom=zoom,
        include_blank_tiles=include_blank_tiles,
        patch=args.patch,
        cache_dir=args.cache_dir,
        output_dir=args.output_dir,
        keep_tiles=args.keep_tiles,
    )
    output_path = FortniteMapBuilder().build(options)

    print()
    print(f"saved final map: {output_path}")
    if args.keep_tiles:
        print(f"downloaded tiles kept in: {options.cache_dir}")
    else:
        print("temporary chunks deleted")


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description="Build a Fortnite map image from fortnite.gg tiles.")
    parser.add_argument(
        "--zoom",
        type=int,
        choices=range(MIN_ZOOM, MAX_ZOOM + 1),
        metavar=f"{MIN_ZOOM}-{MAX_ZOOM}",
        help="zoom level to build",
    )
    parser.add_argument("--patch", default=PATCH, help=f"Fortnite patch to download, default: {PATCH}")

    blank_group = parser.add_mutually_exclusive_group()
    blank_group.add_argument(
        "--include-blanks",
        action="store_true",
        help="render blank map tiles as the fortnite.gg grey background",
    )
    blank_group.add_argument(
        "--transparent-blanks",
        action="store_true",
        help="render blank map tiles as transparent pixels",
    )

    parser.add_argument("--cache-dir", type=Path, default=BuildOptions.cache_dir, help="tile cache directory")
    parser.add_argument("--output-dir", type=Path, default=BuildOptions.output_dir, help="final map output directory")
    parser.add_argument("--keep-tiles", action="store_true", help="keep downloaded tiles after the PNG is built")

    return parser.parse_args(argv)


def resolve_blank_tile_mode(args):
    if args.include_blanks:
        return True
    if args.transparent_blanks:
        return False

    return ask_yes_no("include blank grey squares? (y/n): ")


def ask_zoom():
    print("choose a zoom level:")
    for zoom in range(MIN_ZOOM, MAX_ZOOM + 1):
        resolution = resolution_for_zoom(zoom)
        print(f"  {zoom} - {resolution} x {resolution} px")

    while True:
        value = input("enter zoom level: ").strip()

        try:
            zoom = int(value)
        except ValueError:
            print("enter a number from the list")
            continue

        if MIN_ZOOM <= zoom <= MAX_ZOOM:
            return zoom

        print(f"enter a zoom level from {MIN_ZOOM} to {MAX_ZOOM}")


def ask_yes_no(prompt):
    while True:
        value = input(prompt).strip().lower()

        if value in ("y", "yes"):
            return True
        if value in ("n", "no"):
            return False

        print("enter y or n")
