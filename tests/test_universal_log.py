"""Tests for universal log module."""
import sys, unittest, os, json
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class TestUniversalLog(unittest.TestCase):
    def setUp(self):
        from miner.config import MINING_DIR
        self.log_txt = MINING_DIR / "test_universal_log.txt"
        self.log_json = MINING_DIR / "test_universal_log.json"
        from miner.storage import universal_log
        universal_log.UNIVERSAL_LOG = self.log_txt
        universal_log.UNIVERSAL_JSON = self.log_json
    
    def tearDown(self):
        for f in [self.log_txt, self.log_json]:
            if f.exists():
                os.remove(f)
    
    def test_log_capture_basic(self):
        from miner.storage.universal_log import log_capture
        log_capture("你好", "Hello", "ni3 hao3", "Test", "zh")
        self.assertTrue(self.log_txt.exists())
        self.assertTrue(self.log_json.exists())
    
    def test_log_content_txt(self):
        from miner.storage.universal_log import log_capture
        log_capture("测试句子", "Test sentence", "ce4 shi4 ju4 zi", "Game", "zh")
        with open(self.log_txt, "r", encoding="utf-8") as f:
            content = f.read()
        self.assertIn("测试句子", content)
        self.assertIn("Test sentence", content)
    
    def test_log_content_json(self):
        from miner.storage.universal_log import log_capture
        log_capture("你好", "Hello", "ni3 hao3", "Test", "zh")
        with open(self.log_json, "r", encoding="utf-8") as f:
            entries = json.load(f)
        self.assertEqual(len(entries), 1)
        self.assertEqual(entries[0]["sentence"], "你好")
        self.assertEqual(entries[0]["translation"], "Hello")
    
    def test_log_multiple_entries(self):
        from miner.storage.universal_log import log_capture
        log_capture("第一句", "First", "di4 yi1 ju4", "Test", "zh")
        log_capture("第二句", "Second", "di4 er4 ju4", "Test", "zh")
        with open(self.log_json, "r", encoding="utf-8") as f:
            entries = json.load(f)
        self.assertEqual(len(entries), 2)

if __name__ == '__main__':
    unittest.main()
