import unittest

from fnmap.config import (
    MAX_ZOOM,
    MIN_ZOOM,
    TILE_SIZE,
    full_tile_area,
    get_provider,
    map_tile_area,
    normalize_provider_key,
    resolution_for_zoom,
)


class ConfigTests(unittest.TestCase):
    def test_resolution_for_zoom_scales_by_tile_size(self):
        self.assertEqual(resolution_for_zoom(0), TILE_SIZE)
        self.assertEqual(resolution_for_zoom(7), 32768)

    def test_full_tile_area_covers_expected_tile_count(self):
        area = full_tile_area(3)

        self.assertEqual(area.tile_width, 8)
        self.assertEqual(area.tile_height, 8)
        self.assertEqual(area.pixel_width, 2048)
        self.assertEqual(len(list(area.iter_tiles())), 64)

    def test_map_tile_area_stays_inside_full_area(self):
        area = map_tile_area(MAX_ZOOM)
        full_area = full_tile_area(MAX_ZOOM)

        self.assertGreaterEqual(area.x_start, full_area.x_start)
        self.assertGreaterEqual(area.y_start, full_area.y_start)
        self.assertLessEqual(area.x_end, full_area.x_end)
        self.assertLessEqual(area.y_end, full_area.y_end)

    def test_invalid_zoom_raises(self):
        with self.assertRaises(ValueError):
            full_tile_area(MIN_ZOOM - 1)

        with self.assertRaises(ValueError):
            full_tile_area(MAX_ZOOM + 1)

    def test_provider_url_patterns(self):
        self.assertEqual(get_provider("fortnitegg").referer, "https://fortnite.gg/")
        self.assertEqual(
            get_provider("nadrops").tile_url("41.00", 1, 0, 0),
            "https://hoqugussrmehlscfkpvh.supabase.co/storage/v1/object/public/41.00_br_tiles_v2/1/0/0.webp",
        )
        self.assertEqual(
            get_provider("dropmazter").tile_url("41.00", 1, 0, 0),
            "https://dropmazter.com/wp-content/themes/astra/in_house_maps/41.00/1/0/0.webp",
        )

    def test_provider_aliases(self):
        self.assertEqual(normalize_provider_key("fortnite.gg"), "fortnitegg")
        self.assertEqual(normalize_provider_key("dropmaster"), "dropmazter")

    def test_provider_zoom_validation(self):
        get_provider("fortnitegg").validate_zoom(0)

        with self.assertRaises(ValueError):
            get_provider("nadrops").validate_zoom(0)


if __name__ == "__main__":
    unittest.main()
