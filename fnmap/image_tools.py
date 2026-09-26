from io import BytesIO
import struct
import zlib

from PIL import Image, ImageStat

from .config import BACKGROUND_COLOR, BACKGROUND_TOLERANCE, BACKGROUND_UNIFORMITY_TOLERANCE, TILE_SIZE


def is_background_tile(
    image_data,
    background_color=BACKGROUND_COLOR,
    color_tolerance=BACKGROUND_TOLERANCE,
    uniformity_tolerance=BACKGROUND_UNIFORMITY_TOLERANCE,
):
    with Image.open(BytesIO(image_data)) as image:
        return is_background_image(image, background_color, color_tolerance, uniformity_tolerance)


def is_background_image(
    image,
    background_color=BACKGROUND_COLOR,
    color_tolerance=BACKGROUND_TOLERANCE,
    uniformity_tolerance=BACKGROUND_UNIFORMITY_TOLERANCE,
):
    image = image.convert("RGB")
    stats = ImageStat.Stat(image)

    return all(
        abs(channel_mean - background_color[index]) <= color_tolerance
        and channel_stddev <= uniformity_tolerance
        for index, (channel_mean, channel_stddev) in enumerate(zip(stats.mean, stats.stddev))
    )


def write_streamed_png(output_path, width, height, row_images):
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("wb") as output:
        output.write(b"\x89PNG\r\n\x1a\n")
        _write_chunk(output, b"IHDR", struct.pack(">IIBBBBB", width, height, 8, 6, 0, 0, 0))

        compressor = zlib.compressobj()
        pending = bytearray()
        stride = width * 4

        for row_image in row_images:
            row_image = row_image.convert("RGBA")
            row_data = row_image.tobytes()

            for y in range(row_image.height):
                start = y * stride
                pending.extend(compressor.compress(b"\x00" + row_data[start : start + stride]))

                if len(pending) >= 1024 * 1024:
                    _write_chunk(output, b"IDAT", bytes(pending))
                    pending.clear()

        pending.extend(compressor.flush())
        if pending:
            _write_chunk(output, b"IDAT", bytes(pending))

        _write_chunk(output, b"IEND", b"")


def blank_row(width, include_blank_tiles, background_color=BACKGROUND_COLOR):
    color = background_color + (255,) if include_blank_tiles else (0, 0, 0, 0)
    return Image.new("RGBA", (width, TILE_SIZE), color)


def _write_chunk(output, chunk_type, data):
    output.write(struct.pack(">I", len(data)))
    output.write(chunk_type)
    output.write(data)
    checksum = zlib.crc32(chunk_type)
    checksum = zlib.crc32(data, checksum)
    output.write(struct.pack(">I", checksum & 0xFFFFFFFF))
