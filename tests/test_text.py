"""Tests for text processing - multi-language support."""
import sys, unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class TestText(unittest.TestCase):
    def test_sanitize_unicode(self):
        from miner.text import sanitize_unicode
        self.assertEqual(sanitize_unicode("你好"), "你好")
        self.assertEqual(sanitize_unicode("Über"), "Über")
        self.assertEqual(sanitize_unicode("καλημέρα"), "καλημέρα")
        self.assertEqual(sanitize_unicode("привет"), "привет")
    
    def test_sanitize_unicode_escapes(self):
        from miner.text import sanitize_unicode
        self.assertEqual(sanitize_unicode("\\u4f60\\u597d"), "你好")
        self.assertEqual(sanitize_unicode("\\u00dcber"), "Über")
    
    def test_clean_text(self):
        from miner.text import clean_text
        self.assertEqual(clean_text("  hello  "), "hello")
        self.assertEqual(clean_text("你好  世界"), "你好世界")
        self.assertEqual(clean_text("café   monde"), "café monde")
    
    def test_is_valid_text(self):
        from miner.text import is_valid_text
        self.assertTrue(is_valid_text("你好世界"))
        self.assertTrue(is_valid_text("Hello World"))
        self.assertTrue(is_valid_text("Überprüfung"))
        self.assertTrue(is_valid_text("καλημέρα"))
        self.assertFalse(is_valid_text(""))
        self.assertFalse(is_valid_text("a"))
        self.assertFalse(is_valid_text("[No text detected]"))
    
    def test_split_sentences_cjk(self):
        from miner.text import split_sentences
        sents = split_sentences("你好。世界！")
        self.assertEqual(len(sents), 2)
        self.assertIn("你好。", sents)
        self.assertIn("世界！", sents)
    
    def test_split_sentences_western(self):
        from miner.text import split_sentences
        sents = split_sentences("Hello. World!")
        self.assertEqual(len(sents), 2)
    
    def test_split_sentences_mixed(self):
        from miner.text import split_sentences
        sents = split_sentences("你好。Hello! 世界？")
        self.assertEqual(len(sents), 3)
    
    def test_text_similarity(self):
        from miner.text import text_similarity
        self.assertGreater(text_similarity("hello world", "hello world"), 0.9)
        self.assertLess(text_similarity("hello", "world"), 0.5)
        self.assertEqual(text_similarity("", "test"), 0.0)
    
    def test_is_duplicate(self):
        from miner.text import is_duplicate
        history = ["你好世界", "Hello World"]
        self.assertTrue(is_duplicate("你好世界", history))
        self.assertFalse(is_duplicate("全新句子", history))
    
    def test_load_history_empty(self):
        from miner.text import load_history
        history = load_history()
        self.assertIsInstance(history, list)
    
    def test_get_pinyin(self):
        from miner.text import get_pinyin
        py = get_pinyin("你好")
        self.assertIsInstance(py, str)
        self.assertGreater(len(py), 0)
    
    def test_get_pinyin_tone_marks(self):
        from miner.text import get_pinyin
        py = get_pinyin("你好", tone_marks=True)
        self.assertIsInstance(py, str)
        self.assertGreater(len(py), 0)
    
    def test_format_with_pronunciation_cjk(self):
        from miner.text import format_with_pronunciation
        result = format_with_pronunciation("你好", "zh")
        self.assertIn("你好", result)
        self.assertIn("\n", result)
    
    def test_format_with_pronunciation_latin(self):
        from miner.text import format_with_pronunciation
        result = format_with_pronunciation("Hello World", "en")
        self.assertEqual(result, "Hello World")
    
    def test_format_with_pronunciation_greek(self):
        from miner.text import format_with_pronunciation
        result = format_with_pronunciation("καλημέρα", "el")
        self.assertIn("καλημέρα", result)

if __name__ == '__main__':
    unittest.main()
