"""Tests for new modules: health, stats, backup, glossary, duplicates."""
import sys, unittest, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class TestHealth(unittest.TestCase):
    def test_health_check(self):
        from miner.health import run_health_check
        checks = run_health_check()
        self.assertIn("all_ok", checks)
        self.assertIn("grim", checks)
        self.assertIn("tesseract", checks)

class TestStats(unittest.TestCase):
    def test_record_and_load_stats(self):
        from miner.stats import record_mining, load_stats
        record_mining("zh", True, 85.0)
        stats = load_stats()
        self.assertGreater(stats["total_mined"], 0)

class TestBackup(unittest.TestCase):
    def test_create_backup(self):
        from miner.backup import create_backup, list_backups
        self.assertTrue(create_backup())
        backups = list_backups()
        self.assertGreater(len(backups), 0)

class TestDuplicates(unittest.TestCase):
    def test_normalize_text(self):
        from miner.duplicates import normalize_for_comparison
        self.assertEqual(normalize_for_comparison("你 好 世 界"), "你好世界")
        self.assertEqual(normalize_for_comparison("Hello World"), "hello world")

    def test_is_similar(self):
        from miner.duplicates import is_similar
        self.assertTrue(is_similar("你好世界", "你好世界"))
        self.assertTrue(is_similar("你 好 世 界", "你好世界"))
        self.assertFalse(is_similar("你好", "世界"))

if __name__ == '__main__':
    unittest.main()
