# fnmap

Build high-resolution Fortnite map images from fortnite.gg map tiles.

The current implementation downloads WebP tiles for a selected patch and zoom level, skips blank background tiles when possible, and streams the final PNG to disk row-by-row so very large maps can be produced without holding the full image in memory.

## Features

- Build map images from 256 px up to 32,768 px.
- Choose the Fortnite patch to download.
- Render blank areas either as fortnite.gg grey squares or transparent pixels.
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
```

Useful options:

```text
--zoom 0-7              Build resolution, where 0 is 256 px and 7 is 32,768 px.
--patch PATCH           fortnite.gg patch, for example 40.40.
--include-blanks        Render blank areas as grey background pixels.
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
