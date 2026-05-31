import unittest

from fnmap.cli import parse_args, resolve_blank_tile_mode


class CliTests(unittest.TestCase):
    def test_parse_scripted_build_args(self):
        args = parse_args(["--zoom", "6", "--patch", "40.40", "--transparent-blanks", "--keep-tiles"])

        self.assertEqual(args.zoom, 6)
        self.assertEqual(args.patch, "40.40")
        self.assertTrue(args.transparent_blanks)
        self.assertTrue(args.keep_tiles)

    def test_resolve_blank_tile_mode_from_flags(self):
        self.assertFalse(resolve_blank_tile_mode(parse_args(["--transparent-blanks"])))
        self.assertTrue(resolve_blank_tile_mode(parse_args(["--include-blanks"])))


if __name__ == "__main__":
    unittest.main()
