"""Tests for configuration - multi-language registry."""
import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class TestConfig(unittest.TestCase):
    def test_lang_registry_structure(self):
        from miner.config import LANG_REGISTRY
        for code, info in LANG_REGISTRY.items():
            self.assertIn("tess", info)
            self.assertIn("google", info)
            self.assertIn("name", info)
            self.assertIn("script", info)
            self.assertIn("romaji", info)
    
    def test_lang_registry_cjk(self):
        from miner.config import LANG_REGISTRY
        self.assertEqual(LANG_REGISTRY["zh"]["script"], "cjk")
        self.assertEqual(LANG_REGISTRY["ja"]["script"], "cjk")
        self.assertEqual(LANG_REGISTRY["ko"]["script"], "cjk")
    
    def test_lang_registry_latin(self):
        from miner.config import LANG_REGISTRY
        self.assertEqual(LANG_REGISTRY["de"]["script"], "latin")
        self.assertEqual(LANG_REGISTRY["es"]["script"], "latin")
        self.assertEqual(LANG_REGISTRY["fr"]["script"], "latin")
        self.assertEqual(LANG_REGISTRY["pl"]["script"], "latin")
    
    def test_lang_registry_greek(self):
        from miner.config import LANG_REGISTRY
        self.assertEqual(LANG_REGISTRY["el"]["script"], "greek")
    
    def test_lang_registry_cyrillic(self):
        from miner.config import LANG_REGISTRY
        self.assertEqual(LANG_REGISTRY["ru"]["script"], "cyrillic")
    
    def test_lang_registry_romaji(self):
        from miner.config import LANG_REGISTRY
        self.assertEqual(LANG_REGISTRY["zh"]["romaji"], "pinyin")
        self.assertEqual(LANG_REGISTRY["ja"]["romaji"], "romaji")
        self.assertEqual(LANG_REGISTRY["ko"]["romaji"], "romanization")
        self.assertEqual(LANG_REGISTRY["el"]["romaji"], "transliteration")
        self.assertEqual(LANG_REGISTRY["ru"]["romaji"], "transliteration")
        self.assertIsNone(LANG_REGISTRY["de"]["romaji"])
    
    def test_ocr_langs_backward_compat(self):
        from miner.config import OCR_LANGS, LANG_REGISTRY
        for code, tess in OCR_LANGS.items():
            self.assertEqual(tess, LANG_REGISTRY[code]["tess"])
    
    def test_google_langs_backward_compat(self):
        from miner.config import GOOGLE_LANG_CODES, LANG_REGISTRY
        for code, google in GOOGLE_LANG_CODES.items():
            self.assertEqual(google, LANG_REGISTRY[code]["google"])
    
    def test_mining_dir_exists(self):
        from miner.config import MINING_DIR
        self.assertTrue(MINING_DIR.exists())
    
    def test_all_languages_have_tesseract_codes(self):
        from miner.config import LANG_REGISTRY
        for code, info in LANG_REGISTRY.items():
            self.assertIsInstance(info["tess"], str)
            self.assertGreater(len(info["tess"]), 0)
    
    def test_all_languages_have_google_codes(self):
        from miner.config import LANG_REGISTRY
        for code, info in LANG_REGISTRY.items():
            self.assertIsInstance(info["google"], str)
            self.assertGreater(len(info["google"]), 0)

if __name__ == '__main__':
    unittest.main()
