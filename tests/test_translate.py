"""Tests for translation module - multi-language support."""
import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class TestTranslate(unittest.TestCase):
    def test_translate_chinese_to_english(self):
        from miner.translate import translate_text
        result = translate_text("你好", src="zh", dest="en")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_translate_japanese_to_english(self):
        from miner.translate import translate_text
        result = translate_text("こんにちは", src="ja", dest="en")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_translate_korean_to_english(self):
        from miner.translate import translate_text
        result = translate_text("안녕하세요", src="ko", dest="en")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_translate_german_to_english(self):
        from miner.translate import translate_text
        result = translate_text("Guten Tag", src="de", dest="en")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_translate_spanish_to_english(self):
        from miner.translate import translate_text
        result = translate_text("Hola mundo", src="es", dest="en")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_translate_greek_to_english(self):
        from miner.translate import translate_text
        result = translate_text("καλημέρα", src="el", dest="en")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_translate_french_to_english(self):
        from miner.translate import translate_text
        result = translate_text("Bonjour le monde", src="fr", dest="en")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_translate_polish_to_english(self):
        from miner.translate import translate_text
        result = translate_text("Dzień dobry", src="pl", dest="en")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_translate_russian_to_english(self):
        from miner.translate import translate_text
        result = translate_text("привет", src="ru", dest="en")
        self.assertIsInstance(result, str)
        self.assertGreater(len(result), 0)
    
    def test_translate_empty(self):
        from miner.translate import translate_text
        self.assertEqual(translate_text(""), "")
        self.assertEqual(translate_text("   "), "")
    
    def test_translate_garbage_rejected(self):
        from miner.translate import translate_text
        self.assertEqual(translate_text("E E E", src="zh", dest="en"), "")
        self.assertEqual(translate_text("08", src="de", dest="en"), "")
    
    def test_is_valid_for_translation_cjk(self):
        from miner.translate import _is_valid_for_translation
        self.assertTrue(_is_valid_for_translation("你好世界", "zh"))
        self.assertTrue(_is_valid_for_translation("こんにちは", "ja"))
        self.assertTrue(_is_valid_for_translation("안녕하세요", "ko"))
    
    def test_is_valid_for_translation_latin(self):
        from miner.translate import _is_valid_for_translation
        self.assertTrue(_is_valid_for_translation("Überprüfung", "de"))
        self.assertTrue(_is_valid_for_translation("café", "fr"))
        self.assertTrue(_is_valid_for_translation("Dzień dobry", "pl"))
    
    def test_is_valid_for_translation_greek(self):
        from miner.translate import _is_valid_for_translation
        self.assertTrue(_is_valid_for_translation("καλημέρα", "el"))
    
    def test_is_valid_for_translation_cyrillic(self):
        from miner.translate import _is_valid_for_translation
        self.assertTrue(_is_valid_for_translation("привет", "ru"))
    
    def test_is_valid_for_translation_rejects_garbage(self):
        from miner.translate import _is_valid_for_translation
        self.assertFalse(_is_valid_for_translation("", "zh"))
        self.assertFalse(_is_valid_for_translation("E", "zh"))
        self.assertFalse(_is_valid_for_translation("E E E", "zh"))
        self.assertFalse(_is_valid_for_translation("08", "de"))
    
    def test_copy_to_clipboard(self):
        from miner.translate import copy_to_clipboard
        import subprocess
        copy_to_clipboard("test clipboard content")
        result = subprocess.run(["wl-paste"], capture_output=True, text=True)
        self.assertIn("test clipboard content", result.stdout)
    
    def test_notify(self):
        from miner.translate import notify
        notify("Test", "Notification test", timeout=1000)
    
    def test_find_best_audio_source(self):
        from miner.translate import _find_best_audio_source
        source = _find_best_audio_source()
        self.assertIsInstance(source, str)
        self.assertGreater(len(source), 0)

if __name__ == '__main__':
    unittest.main()
