import unittest
from unittest.mock import Mock

from fnmap.builder import FortniteMapBuilder
from fnmap.config import get_provider


class BuilderTests(unittest.TestCase):
    def test_fortnitegg_fetch_uses_browser_image_headers(self):
        builder = FortniteMapBuilder()
        response = Mock()
        response.headers = {"content-type": "image/webp"}
        response.content = b"tile"
        builder.session.get = Mock(return_value=response)

        result = builder._fetch_tile(get_provider("fortnitegg"), "42.03", 3, 0, 0)

        self.assertEqual(result, b"tile")
        self.assertIn("image/webp", builder.session.headers["Accept"])
        builder.session.get.assert_called_once_with(
            "https://fortnite.gg/maps/42.03/3/0/0.webp",
            headers={"Referer": "https://fortnite.gg/"},
            timeout=30,
        )
        response.raise_for_status.assert_called_once_with()


if __name__ == "__main__":
    unittest.main()
