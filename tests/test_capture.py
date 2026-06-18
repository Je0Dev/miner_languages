"""Tests for capture module."""
import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class TestCapture(unittest.TestCase):
    def test_parse_slurp_geom_standard(self):
        from miner.capture import parse_slurp_geom
        geom = parse_slurp_geom("100,100,200,50")
        self.assertEqual(geom, (100, 100, 200, 50))
    
    def test_parse_slurp_geom_slurp_format(self):
        from miner.capture import parse_slurp_geom
        geom = parse_slurp_geom("100,100 200x50")
        self.assertEqual(geom, (100, 100, 200, 50))
    
    def test_parse_slurp_geom_imagemagick(self):
        from miner.capture import parse_slurp_geom
        geom = parse_slurp_geom("200x50+100+100")
        self.assertEqual(geom, (100, 100, 200, 50))
    
    def test_parse_slurp_geom_invalid(self):
        from miner.capture import parse_slurp_geom
        geom = parse_slurp_geom("invalid")
        self.assertIsNone(geom)
    
    def test_get_display_scale(self):
        from miner.capture import get_display_scale
        scale = get_display_scale()
        self.assertIsInstance(scale, float)
        self.assertGreater(scale, 0)
    
    def test_capture_region_imports(self):
        from miner.capture import capture_region
        self.assertTrue(callable(capture_region))
    
    def test_capture_screenshot_imports(self):
        from miner.capture import capture_screenshot
        self.assertTrue(callable(capture_screenshot))

if __name__ == '__main__':
    unittest.main()
