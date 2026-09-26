import tempfile
import unittest
from pathlib import Path

from PIL import Image

from fnmap.config import BACKGROUND_COLOR, TILE_SIZE
from fnmap.image_tools import blank_row, is_background_image, write_streamed_png


class ImageToolsTests(unittest.TestCase):
    def test_background_image_detection(self):
        image = Image.new("RGB", (TILE_SIZE, TILE_SIZE), BACKGROUND_COLOR)

        self.assertTrue(is_background_image(image))

    def test_non_background_image_detection(self):
        image = Image.new("RGB", (TILE_SIZE, TILE_SIZE), (255, 0, 0))

        self.assertFalse(is_background_image(image))

    def test_blank_row_can_be_transparent(self):
        row = blank_row(TILE_SIZE, include_blank_tiles=False)

        self.assertEqual(row.getpixel((0, 0)), (0, 0, 0, 0))

    def test_blank_row_uses_provider_background(self):
        row = blank_row(TILE_SIZE, include_blank_tiles=True, background_color=(40, 49, 64))

        self.assertEqual(row.getpixel((0, 0)), (40, 49, 64, 255))

    def test_write_streamed_png_writes_valid_png(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "map.png"
            rows = [Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (1, 2, 3, 255))]

            write_streamed_png(output_path, TILE_SIZE, TILE_SIZE, rows)

            with Image.open(output_path) as image:
                self.assertEqual(image.format, "PNG")
                self.assertEqual(image.size, (TILE_SIZE, TILE_SIZE))
                self.assertEqual(image.mode, "RGBA")


if __name__ == "__main__":
    unittest.main()
