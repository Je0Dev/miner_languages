"""Tests for Anki CSV export module."""
import sys, unittest, json, os
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class TestAnkiExport(unittest.TestCase):
    def setUp(self):
        from miner.config import MINING_DIR, SENTENCES_FILE
        self.test_csv = MINING_DIR / "test_anki_export.csv"
        self.test_json = MINING_DIR / "test_sentences.json"
        self.entries = [
            {"sentence": "你好", "translation": "Hello", "pinyin": "ni3 hao3",
             "audio": "", "source": "Test", "timestamp": "20260516_120000"},
            {"sentence": "世界", "translation": "World", "pinyin": "shi4 jie4",
             "audio": "", "source": "Test", "timestamp": "20260516_120001"},
        ]
        with open(self.test_json, "w", encoding="utf-8") as f:
            json.dump(self.entries, f)
    
    def tearDown(self):
        for f in [self.test_csv, self.test_json]:
            if f.exists():
                os.remove(f)
    
    def test_export_to_anki_csv(self):
        from miner.storage.anki import export_to_anki_csv
        from miner.config import MINING_DIR, SENTENCES_FILE
        # Temporarily override
        from miner.storage import anki as anki_export
        orig_json = anki_export.MINING_DIR
        anki_export.MINING_DIR = MINING_DIR
        anki_export.SENTENCES_FILE = Path("test_sentences.json")
        anki_export.ANKI_CSV = self.test_csv
        
        count = export_to_anki_csv(self.test_csv)
        self.assertEqual(count, 2)
        self.assertTrue(self.test_csv.exists())
        
        # Restore
        anki_export.MINING_DIR = orig_json
    
    def test_append_to_anki_csv(self):
        from miner.storage.anki import append_to_anki_csv
        entry = {"sentence": "测试", "translation": "Test", "pinyin": "ce4 shi4",
                 "audio": "", "source": "Test", "timestamp": "20260516_120002"}
        result = append_to_anki_csv(entry, self.test_csv)
        self.assertTrue(result)
        self.assertTrue(self.test_csv.exists())

if __name__ == '__main__':
    unittest.main()
