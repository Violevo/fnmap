# fnmap

Build high-resolution Fortnite map images from web map tiles.

The current implementation downloads WebP tiles from fortnite.gg, nadrops, or dropmazter for a selected patch and zoom level, skips blank background tiles when possible, and streams the final PNG to disk row-by-row so very large maps can be produced without holding the full image in memory.

## Features

- Build map images from 256 px up to 32,768 px.
- Choose the tile provider and Fortnite patch to download.
- Render blank areas either as the provider background or transparent pixels.
- Use the interactive prompts or pass CLI flags for repeatable builds.
- Optionally keep downloaded tiles for debugging or reuse.

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
```

On macOS or Linux:

```sh
python3 -m venv .venv
./.venv/bin/python -m pip install -r requirements.txt
```

## Usage

Interactive mode:

```powershell
.\.venv\Scripts\python.exe main.py
```

Scripted mode:

```powershell
.\.venv\Scripts\python.exe main.py --zoom 6 --patch 40.40 --transparent-blanks
.\.venv\Scripts\python.exe main.py --provider nadrops --zoom 7 --patch 41.00 --transparent-blanks
.\.venv\Scripts\python.exe main.py --provider dropmazter --zoom 7 --patch 41.00 --include-blanks
```

Useful options:

```text
--provider PROVIDER     Tile provider: fortnitegg, nadrops, or dropmazter.
--zoom ZOOM             Build resolution. fortnitegg supports 0-7; nadrops and dropmazter support 1-7.
--patch PATCH           Fortnite patch, for example 41.00. Defaults depend on the provider.
--include-blanks        Render blank areas as provider background pixels.
--transparent-blanks    Render blank areas as transparent pixels.
--cache-dir PATH        Directory for temporary downloaded tiles.
--output-dir PATH       Directory for generated PNG files.
--keep-tiles            Keep downloaded tile files after the PNG is built.
```

Generated files are written to `output/maps/` by default. Tile downloads are stored under `cache/tiles/` while the build runs.

## Tests

```powershell
.\.venv\Scripts\python.exe -m unittest discover
```

## License

MIT
