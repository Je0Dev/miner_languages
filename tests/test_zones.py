"""Tests for zone management."""
import sys, unittest, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class TestZones(unittest.TestCase):
    def test_save_and_load_zone(self):
        from miner.zones import save_zone, get_zone, delete_zone
        self.assertTrue(save_zone("test_zone", "100,100 200x50", "zh"))
        zone = get_zone("test_zone")
        self.assertIsNotNone(zone)
        self.assertEqual(zone["geom"], "100,100 200x50")
        self.assertEqual(zone["lang"], "zh")
        self.assertTrue(delete_zone("test_zone"))
        self.assertIsNone(get_zone("test_zone"))

    def test_list_zones(self):
        from miner.zones import save_zone, list_zones, delete_zone
        save_zone("zone_a", "0,0 100x50", "ja")
        save_zone("zone_b", "100,100 200x50", "de")
        zones = list_zones()
        self.assertIn("zone_a", zones)
        self.assertIn("zone_b", zones)
        delete_zone("zone_a")
        delete_zone("zone_b")

    def test_delete_nonexistent_zone(self):
        from miner.zones import delete_zone
        self.assertFalse(delete_zone("nonexistent"))

    def test_get_nonexistent_zone(self):
        from miner.zones import get_zone
        self.assertIsNone(get_zone("nonexistent"))

if __name__ == '__main__':
    unittest.main()
