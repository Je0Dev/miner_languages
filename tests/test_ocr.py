"""Tests for OCR module - multi-language support."""
import sys, unittest
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

def _get_font(size=24):
    for path in ["/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
                 "/usr/share/fonts/noto/NotoSans-Regular.ttf",
                 "/usr/share/fonts/TTF/DejaVuSans.ttf"]:
        try: return ImageFont.truetype(path, size)
        except: pass
    return ImageFont.load_default()

class TestOCR(unittest.TestCase):
    def test_prewarm_tesseract(self):
        from miner.ocr import prewarm_tesseract
        for lang in ["eng", "chi_sim", "jpn", "kor", "deu", "spa", "ell", "fra", "pol", "rus"]:
            prewarm_tesseract(lang)
    
    def test_ocr_english(self):
        from miner.ocr import ocr_image
        img = Image.new('L', (300, 60), 255)
        draw = ImageDraw.Draw(img)
        draw.text((20, 15), 'Hello World', font=_get_font(24), fill=0)
        img.save('/tmp/test_ocr_en.png')
        text = ocr_image(Path('/tmp/test_ocr_en.png'), 'en')
        self.assertGreater(len(text), 0)
    
    def test_ocr_german_umlauts(self):
        from miner.ocr import ocr_image
        img = Image.new('L', (300, 60), 255)
        draw = ImageDraw.Draw(img)
        draw.text((20, 15), 'Überprüfung', font=_get_font(24), fill=0)
        img.save('/tmp/test_ocr_de.png')
        text = ocr_image(Path('/tmp/test_ocr_de.png'), 'de')
        self.assertGreater(len(text), 0)
    
    def test_ocr_chinese(self):
        from miner.ocr import ocr_image
        img = Image.new('L', (400, 100), 255)
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), '你好世界', font=_get_font(32), fill=0)
        img.save('/tmp/test_ocr_zh.png')
        text = ocr_image(Path('/tmp/test_ocr_zh.png'), 'zh')
        self.assertGreater(len(text), 0)
    
    def test_ocr_japanese(self):
        from miner.ocr import ocr_image
        img = Image.new('L', (400, 100), 255)
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), 'こんにちは', font=_get_font(32), fill=0)
        img.save('/tmp/test_ocr_ja.png')
        text = ocr_image(Path('/tmp/test_ocr_ja.png'), 'ja')
        self.assertGreater(len(text), 0)
    
    def test_ocr_korean(self):
        from miner.ocr import ocr_image
        img = Image.new('L', (400, 100), 255)
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), '안녕하세요', font=_get_font(32), fill=0)
        img.save('/tmp/test_ocr_ko.png')
        text = ocr_image(Path('/tmp/test_ocr_ko.png'), 'ko')
        self.assertGreater(len(text), 0)
    
    def test_ocr_german_umlauts(self):
        from miner.ocr import ocr_image
        img = Image.new('L', (300, 60), 255)
        draw = ImageDraw.Draw(img)
        draw.text((20, 15), 'Überprüfung', fill=0)
        img.save('/tmp/test_ocr_de.png')
        text = ocr_image(Path('/tmp/test_ocr_de.png'), 'de')
        self.assertGreater(len(text), 0)
    
    def test_ocr_greek(self):
        from miner.ocr import ocr_image
        img = Image.new('L', (400, 100), 255)
        draw = ImageDraw.Draw(img)
        draw.text((20, 20), 'καλημέρα', font=_get_font(32), fill=0)
        img.save('/tmp/test_ocr_el.png')
        text = ocr_image(Path('/tmp/test_ocr_el.png'), 'el')
        self.assertGreater(len(text), 0)
    
    def test_ocr_filter_garbage_cjk(self):
        from miner.ocr import _filter_garbage
        self.assertEqual(_filter_garbage("E", "zh"), "")
        self.assertEqual(_filter_garbage("08", "zh"), "")
        self.assertEqual(_filter_garbage("123", "zh"), "")
        self.assertEqual(_filter_garbage("你好世界", "zh"), "你好世界")
    
    def test_ocr_filter_garbage_latin(self):
        from miner.ocr import _filter_garbage
        self.assertEqual(_filter_garbage("08", "de"), "")
        self.assertEqual(_filter_garbage("12", "es"), "")
        self.assertEqual(_filter_garbage("Überprüfung", "de"), "Überprüfung")
        self.assertEqual(_filter_garbage("café", "fr"), "café")
    
    def test_ocr_filter_garbage_greek(self):
        from miner.ocr import _filter_garbage
        self.assertEqual(_filter_garbage("08", "el"), "")
        self.assertEqual(_filter_garbage("καλημέρα", "el"), "καλημέρα")
    
    def test_ocr_filter_garbage_cyrillic(self):
        from miner.ocr import _filter_garbage
        self.assertEqual(_filter_garbage("08", "ru"), "")
        self.assertEqual(_filter_garbage("привет", "ru"), "привет")
    
    def test_ocr_ensure_utf8(self):
        from miner.ocr import _ensure_utf8
        self.assertEqual(_ensure_utf8(""), "")
        self.assertEqual(_ensure_utf8("你好"), "你好")
        self.assertEqual(_ensure_utf8("Hello"), "Hello")
        self.assertEqual(_ensure_utf8("Über"), "Über")
        self.assertEqual(_ensure_utf8("καλημέρα"), "καλημέρα")
    
    def test_ocr_empty_image(self):
        from miner.ocr import ocr_image
        img = Image.new('L', (50, 50), 255)
        img.save('/tmp/test_ocr_empty.png')
        text = ocr_image(Path('/tmp/test_ocr_empty.png'), 'en')
        self.assertIsInstance(text, str)
    
    def test_ocr_preprocess(self):
        from miner.ocr import preprocess_image
        img = Image.new('L', (100, 50), 200)
        img.save('/tmp/test_preprocess.png')
        result = preprocess_image(Path('/tmp/test_preprocess.png'), 'zh')
        self.assertEqual(result.mode, 'L')
        # CJK upscaling is 3x for small images
        self.assertIn(result.size, [(100, 50), (200, 100), (300, 150)])

if __name__ == '__main__':
    unittest.main()
