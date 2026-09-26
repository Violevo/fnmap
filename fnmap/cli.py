import argparse
from pathlib import Path

from .builder import BuildOptions, FortniteMapBuilder
from .config import TILE_PROVIDERS, get_provider, normalize_provider_key, resolution_for_zoom


def main(argv=None):
    args = parse_args(argv)

    print("Fortnite map builder")
    provider_key = args.provider if args.provider is not None else ask_provider()
    provider = get_provider(provider_key)
    patch = args.patch if args.patch is not None else provider.default_patch

    print(f"Provider: {provider.label}")
    print(f"Patch: {patch}")
    print()

    zoom = args.zoom if args.zoom is not None else ask_zoom(provider)
    try:
        provider.validate_zoom(zoom)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    include_blank_tiles = resolve_blank_tile_mode(args)

    options = BuildOptions(
        zoom=zoom,
        include_blank_tiles=include_blank_tiles,
        provider=provider.key,
        patch=patch,
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
    parser = argparse.ArgumentParser(description="Build a Fortnite map image from web map tiles.")
    parser.add_argument(
        "--provider",
        type=parse_provider,
        help="tile provider to use: fortnitegg, nadrops, or dropmazter",
    )
    parser.add_argument(
        "--zoom",
        type=int,
        metavar="ZOOM",
        help="zoom level to build",
    )
    parser.add_argument("--patch", help="Fortnite patch to download; default depends on provider")

    blank_group = parser.add_mutually_exclusive_group()
    blank_group.add_argument(
        "--include-blanks",
        action="store_true",
        help="render blank map tiles as the provider background",
    )
    blank_group.add_argument(
        "--transparent-blanks",
        action="store_true",
        help="render blank map tiles as transparent pixels",
    )

    parser.add_argument("--cache-dir", type=Path, default=BuildOptions.cache_dir, help="tile cache directory")
    parser.add_argument("--output-dir", type=Path, default=BuildOptions.output_dir, help="final map output directory")
    parser.add_argument("--keep-tiles", action="store_true", help="keep downloaded tiles after the PNG is built")

    args = parser.parse_args(argv)
    if args.provider is not None and args.zoom is not None:
        try:
            get_provider(args.provider).validate_zoom(args.zoom)
        except ValueError as exc:
            parser.error(str(exc))

    return args


def parse_provider(value):
    try:
        return normalize_provider_key(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError(str(exc)) from exc


def resolve_blank_tile_mode(args):
    if args.include_blanks:
        return True
    if args.transparent_blanks:
        return False

    return ask_yes_no("include blank background tiles? (y/n): ")


def ask_provider():
    print("choose a map provider:")
    providers = list(TILE_PROVIDERS.values())
    for index, provider in enumerate(providers, start=1):
        print(
            f"  {index} - {provider.label} "
            f"(default patch {provider.default_patch}, zoom {provider.min_zoom}-{provider.max_zoom})"
        )

    while True:
        value = input("enter provider: ").strip()

        if value.isdigit():
            provider_index = int(value) - 1
            if 0 <= provider_index < len(providers):
                return providers[provider_index].key

        try:
            return normalize_provider_key(value)
        except ValueError:
            print("enter a provider name or number from the list")


def ask_zoom(provider):
    print("choose a zoom level:")
    for zoom in range(provider.min_zoom, provider.max_zoom + 1):
        resolution = resolution_for_zoom(zoom)
        print(f"  {zoom} - {resolution} x {resolution} px")

    while True:
        value = input("enter zoom level: ").strip()

        try:
            zoom = int(value)
        except ValueError:
            print("enter a number from the list")
            continue

        if provider.min_zoom <= zoom <= provider.max_zoom:
            return zoom

        print(f"enter a zoom level from {provider.min_zoom} to {provider.max_zoom}")


def ask_yes_no(prompt):
    while True:
        value = input(prompt).strip().lower()

        if value in ("y", "yes"):
            return True
        if value in ("n", "no"):
            return False

        print("enter y or n")
