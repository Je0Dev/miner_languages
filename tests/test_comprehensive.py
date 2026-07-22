#!/usr/bin/env python3
"""Comprehensive multi-language test suite for Game Sentence Miner v2.
Tests OCR, translation, garbage filtering, and edge cases for all 10 languages."""

import sys, unittest, os, time, re
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

TEST_IMG_DIR = Path("/tmp/miner_comprehensive_tests")
TEST_IMG_DIR.mkdir(exist_ok=True)

LANGS = ["zh", "ja", "ko", "de", "es", "el", "fr", "pl", "ru", "en"]

GAME_PHRASES = {
    "zh": ["你已完成任务", "获得新物品", "等级提升"],
    "ja": ["クエスト完了", "新しいアイテム入手", "レベルアップ"],
    "ko": ["퀘스트 완료", "새 아이템 획득", "레벨 업"],
    "de": ["Quest abgeschlossen", "Neues Item erhalten", "Level aufgestiegen"],
    "es": ["Misión completada", "Nuevo objeto obtenido", "Nivel subido"],
    "el": ["Αποστολή ολοκληρώθηκε", "Νέο αντικείμενο", "Επίπεδο αυξήθηκε"],
    "fr": ["Mission accomplie", "Nouvel objet obtenu", "Niveau augmenté"],
    "pl": ["Zadanie ukończone", "Nowy przedmiot", "Poziom wzrósł"],
    "ru": ["Задание выполнено", "Получен новый предмет", "Уровень повышен"],
    "en": ["Quest completed", "New item acquired", "Level up"],
}


def _get_font(size=24):
    for path in [
        "/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/noto-cjk/NotoSansCJKsc-Regular.otf",
        "/usr/share/fonts/noto/NotoSans-Regular.ttf",
        "/usr/share/fonts/TTF/DejaVuSans.ttf",
        "/usr/share/fonts/truetype/noto/NotoSans-Regular.ttf",
    ]:
        try:
            return ImageFont.truetype(path, size)
        except Exception:
            pass
    return ImageFont.load_default()


def _create_test_image(
    text, width=400, height=80, bg=255, fg=0, font_size=24, fname=None
):
    img = Image.new("L", (width, height), bg)
    draw = ImageDraw.Draw(img)
    font = _get_font(font_size)
    bbox = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = max(10, (width - tw) // 2)
    y = max(5, (height - th) // 2)
    draw.text((x, y), text, font=font, fill=fg)
    if fname is None:
        fname = f"test_{int(time.time() * 1000)}.png"
    path = TEST_IMG_DIR / fname
    img.save(path)
    return path


def _create_dark_bg_image(text, font_size=24, fname=None):
    return _create_test_image(text, bg=20, fg=240, font_size=font_size, fname=fname)


def _create_small_text_image(text, fname=None):
    return _create_test_image(text, font_size=16, fname=fname)


def _create_medium_text_image(text, fname=None):
    return _create_test_image(text, font_size=24, fname=fname)


def _create_shadow_image(text, fname=None):
    img = Image.new("L", (500, 100), 255)
    draw = ImageDraw.Draw(img)
    font = _get_font(24)
    draw.text((22, 22), text, font=font, fill=180)
    draw.text((20, 20), text, font=font, fill=0)
    path = TEST_IMG_DIR / (fname or f"shadow_{int(time.time() * 1000)}.png")
    img.save(path)
    return path


class TestOCRMultilanguage(unittest.TestCase):
    """OCR tests with game-like conditions for all 10 languages."""

    def _test_ocr_lang(self, lang, text, desc=""):
        path = _create_test_image(text, fname=f"ocr_{lang}_{desc}.png")
        from miner.ocr import ocr_image

        result = ocr_image(path, lang)
        return result, text

    def test_zh_dark_bg(self):
        for phrase in GAME_PHRASES["zh"]:
            path = _create_dark_bg_image(phrase, fname=f"zh_dark_{phrase[:4]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "zh")
            self.assertGreater(len(result), 0, f"ZH dark bg failed for: {phrase}")

    def test_zh_small_text(self):
        for phrase in GAME_PHRASES["zh"]:
            path = _create_small_text_image(phrase, fname=f"zh_small_{phrase[:4]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "zh")
            self.assertGreater(len(result), 0, f"ZH small text failed for: {phrase}")

    def test_zh_medium_text(self):
        for phrase in GAME_PHRASES["zh"]:
            path = _create_medium_text_image(phrase, fname=f"zh_med_{phrase[:4]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "zh")
            self.assertGreater(len(result), 0, f"ZH medium text failed for: {phrase}")

    def test_zh_shadow(self):
        for phrase in GAME_PHRASES["zh"]:
            path = _create_shadow_image(phrase, fname=f"zh_shadow_{phrase[:4]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "zh")
            self.assertGreater(len(result), 0, f"ZH shadow failed for: {phrase}")

    def test_ja_dark_bg(self):
        for phrase in GAME_PHRASES["ja"]:
            path = _create_dark_bg_image(phrase, fname=f"ja_dark_{phrase[:4]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "ja")
            self.assertGreater(len(result), 0, f"JA dark bg failed for: {phrase}")

    def test_ja_small_text(self):
        for phrase in GAME_PHRASES["ja"]:
            path = _create_small_text_image(phrase, fname=f"ja_small_{phrase[:4]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "ja")
            self.assertGreater(len(result), 0, f"JA small text failed for: {phrase}")

    def test_ja_medium_text(self):
        for phrase in GAME_PHRASES["ja"]:
            path = _create_medium_text_image(phrase, fname=f"ja_med_{phrase[:4]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "ja")
            self.assertGreater(len(result), 0, f"JA medium text failed for: {phrase}")

    def test_ko_dark_bg(self):
        for phrase in GAME_PHRASES["ko"]:
            path = _create_dark_bg_image(phrase, fname=f"ko_dark_{phrase[:4]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "ko")
            self.assertGreater(len(result), 0, f"KO dark bg failed for: {phrase}")

    def test_ko_small_text(self):
        for phrase in GAME_PHRASES["ko"]:
            path = _create_small_text_image(phrase, fname=f"ko_small_{phrase[:4]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "ko")
            self.assertGreater(len(result), 0, f"KO small text failed for: {phrase}")

    def test_ko_medium_text(self):
        for phrase in GAME_PHRASES["ko"]:
            path = _create_medium_text_image(phrase, fname=f"ko_med_{phrase[:4]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "ko")
            self.assertGreater(len(result), 0, f"KO medium text failed for: {phrase}")

    def test_de_dark_bg(self):
        for phrase in GAME_PHRASES["de"]:
            path = _create_dark_bg_image(phrase, fname=f"de_dark_{phrase[:6]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "de")
            self.assertGreater(len(result), 0, f"DE dark bg failed for: {phrase}")

    def test_de_small_text(self):
        for phrase in GAME_PHRASES["de"]:
            path = _create_small_text_image(phrase, fname=f"de_small_{phrase[:6]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "de")
            self.assertGreater(len(result), 0, f"DE small text failed for: {phrase}")

    def test_es_dark_bg(self):
        for phrase in GAME_PHRASES["es"]:
            path = _create_dark_bg_image(phrase, fname=f"es_dark_{phrase[:6]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "es")
            self.assertGreater(len(result), 0, f"ES dark bg failed for: {phrase}")

    def test_es_small_text(self):
        for phrase in GAME_PHRASES["es"]:
            path = _create_small_text_image(phrase, fname=f"es_small_{phrase[:6]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "es")
            self.assertGreater(len(result), 0, f"ES small text failed for: {phrase}")

    def test_el_dark_bg(self):
        for phrase in GAME_PHRASES["el"]:
            path = _create_dark_bg_image(phrase, fname=f"el_dark_{phrase[:6]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "el")
            self.assertGreater(len(result), 0, f"EL dark bg failed for: {phrase}")

    def test_el_small_text(self):
        for phrase in GAME_PHRASES["el"]:
            path = _create_small_text_image(phrase, fname=f"el_small_{phrase[:6]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "el")
            self.assertGreater(len(result), 0, f"EL small text failed for: {phrase}")

    def test_fr_dark_bg(self):
        for phrase in GAME_PHRASES["fr"]:
            path = _create_dark_bg_image(phrase, fname=f"fr_dark_{phrase[:6]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "fr")
            self.assertGreater(len(result), 0, f"FR dark bg failed for: {phrase}")

    def test_fr_small_text(self):
        for phrase in GAME_PHRASES["fr"]:
            path = _create_small_text_image(phrase, fname=f"fr_small_{phrase[:6]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "fr")
            self.assertGreater(len(result), 0, f"FR small text failed for: {phrase}")

    def test_pl_dark_bg(self):
        for phrase in GAME_PHRASES["pl"]:
            path = _create_dark_bg_image(phrase, fname=f"pl_dark_{phrase[:6]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "pl")
            self.assertGreater(len(result), 0, f"PL dark bg failed for: {phrase}")

    def test_pl_small_text(self):
        for phrase in GAME_PHRASES["pl"]:
            path = _create_small_text_image(phrase, fname=f"pl_small_{phrase[:6]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "pl")
            self.assertGreater(len(result), 0, f"PL small text failed for: {phrase}")

    def test_ru_dark_bg(self):
        for phrase in GAME_PHRASES["ru"]:
            path = _create_dark_bg_image(phrase, fname=f"ru_dark_{phrase[:6]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "ru")
            self.assertGreater(len(result), 0, f"RU dark bg failed for: {phrase}")

    def test_ru_small_text(self):
        for phrase in GAME_PHRASES["ru"]:
            path = _create_small_text_image(phrase, fname=f"ru_small_{phrase[:6]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "ru")
            self.assertGreater(len(result), 0, f"RU small text failed for: {phrase}")

    def test_en_dark_bg(self):
        for phrase in GAME_PHRASES["en"]:
            path = _create_dark_bg_image(phrase, fname=f"en_dark_{phrase[:6]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "en")
            self.assertGreater(len(result), 0, f"EN dark bg failed for: {phrase}")

    def test_en_small_text(self):
        for phrase in GAME_PHRASES["en"]:
            path = _create_small_text_image(phrase, fname=f"en_small_{phrase[:6]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "en")
            self.assertGreater(len(result), 0, f"EN small text failed for: {phrase}")

    def test_en_medium_text(self):
        for phrase in GAME_PHRASES["en"]:
            path = _create_medium_text_image(phrase, fname=f"en_med_{phrase[:6]}.png")
            from miner.ocr import ocr_image

            result = ocr_image(path, "en")
            self.assertGreater(len(result), 0, f"EN medium text failed for: {phrase}")


class TestTranslationMultilanguage(unittest.TestCase):
    """Translation quality tests with game dialogue phrases."""

    def _test_translate(self, lang, phrase):
        from miner.translate import translate_text

        result = translate_text(phrase, src=lang, dest="en")
        return result

    def _check_translation(self, result, phrase, lang):
        self.assertIsNotNone(result, f"{lang} translation failed for: {phrase}")
        self.assertGreater(len(result), 0, f"{lang} translation empty for: {phrase}")

    def test_zh_translation(self):
        for phrase in GAME_PHRASES["zh"]:
            result = self._test_translate("zh", phrase)
            self._check_translation(result, phrase, "ZH")
            print(f"  ZH: '{phrase}' -> '{result}'")

    def test_ja_translation(self):
        for phrase in GAME_PHRASES["ja"]:
            result = self._test_translate("ja", phrase)
            self._check_translation(result, phrase, "JA")
            print(f"  JA: '{phrase}' -> '{result}'")

    def test_ko_translation(self):
        for phrase in GAME_PHRASES["ko"]:
            result = self._test_translate("ko", phrase)
            self._check_translation(result, phrase, "KO")
            print(f"  KO: '{phrase}' -> '{result}'")

    def test_de_translation(self):
        for phrase in GAME_PHRASES["de"]:
            result = self._test_translate("de", phrase)
            self._check_translation(result, phrase, "DE")
            print(f"  DE: '{phrase}' -> '{result}'")

    def test_es_translation(self):
        for phrase in GAME_PHRASES["es"]:
            result = self._test_translate("es", phrase)
            self._check_translation(result, phrase, "ES")
            print(f"  ES: '{phrase}' -> '{result}'")

    def test_el_translation(self):
        for phrase in GAME_PHRASES["el"]:
            result = self._test_translate("el", phrase)
            self._check_translation(result, phrase, "EL")
            print(f"  EL: '{phrase}' -> '{result}'")

    def test_fr_translation(self):
        for phrase in GAME_PHRASES["fr"]:
            result = self._test_translate("fr", phrase)
            self._check_translation(result, phrase, "FR")
            print(f"  FR: '{phrase}' -> '{result}'")

    def test_pl_translation(self):
        for phrase in GAME_PHRASES["pl"]:
            result = self._test_translate("pl", phrase)
            self._check_translation(result, phrase, "PL")
            print(f"  PL: '{phrase}' -> '{result}'")

    def test_ru_translation(self):
        for phrase in GAME_PHRASES["ru"]:
            result = self._test_translate("ru", phrase)
            self._check_translation(result, phrase, "RU")
            print(f"  RU: '{phrase}' -> '{result}'")

    def test_en_translation(self):
        for phrase in GAME_PHRASES["en"]:
            result = self._test_translate("en", phrase)
            self._check_translation(result, phrase, "EN")
            print(f"  EN: '{phrase}' -> '{result}'")


class TestGarbageFiltering(unittest.TestCase):
    """Garbage filtering tests for all languages."""

    def test_reject_numbers_cjk(self):
        from miner.ocr import _filter_garbage

        for lang in ["zh", "ja", "ko"]:
            self.assertEqual(
                _filter_garbage("08", lang), "", f"{lang}: should reject '08'"
            )
            self.assertEqual(
                _filter_garbage("12", lang), "", f"{lang}: should reject '12'"
            )
            self.assertEqual(
                _filter_garbage("123", lang), "", f"{lang}: should reject '123'"
            )

    def test_reject_numbers_latin(self):
        from miner.ocr import _filter_garbage

        for lang in ["de", "es", "fr", "pl", "en"]:
            self.assertEqual(
                _filter_garbage("08", lang), "", f"{lang}: should reject '08'"
            )
            self.assertEqual(
                _filter_garbage("12", lang), "", f"{lang}: should reject '12'"
            )

    def test_reject_numbers_greek(self):
        from miner.ocr import _filter_garbage

        self.assertEqual(_filter_garbage("08", "el"), "")
        self.assertEqual(_filter_garbage("12", "el"), "")

    def test_reject_numbers_cyrillic(self):
        from miner.ocr import _filter_garbage

        self.assertEqual(_filter_garbage("08", "ru"), "")
        self.assertEqual(_filter_garbage("12", "ru"), "")

    def test_reject_single_letters_cjk(self):
        from miner.ocr import _filter_garbage

        for lang in ["zh", "ja", "ko"]:
            self.assertEqual(
                _filter_garbage("E", lang), "", f"{lang}: should reject single 'E'"
            )
            self.assertEqual(
                _filter_garbage("A", lang), "", f"{lang}: should reject single 'A'"
            )

    def test_reject_copyright_cjk(self):
        from miner.ocr import _filter_garbage

        for lang in ["zh", "ja", "ko"]:
            self.assertEqual(
                _filter_garbage("©", lang), "", f"{lang}: should reject copyright"
            )
            result = _filter_garbage("你好©", lang)
            self.assertNotIn("©", result, f"{lang}: copyright should be stripped")

    def test_reject_copyright_latin(self):
        from miner.ocr import _filter_garbage

        for lang in ["de", "es", "fr", "pl", "en"]:
            result = _filter_garbage("Test©", lang)
            self.assertNotIn("©", result, f"{lang}: copyright should be stripped")

    def test_reject_copyright_greek(self):
        from miner.ocr import _filter_garbage

        result = _filter_garbage("αβ©", "el")
        self.assertNotIn("©", result, "EL: copyright should be stripped")

    def test_reject_copyright_cyrillic(self):
        from miner.ocr import _filter_garbage

        result = _filter_garbage("аб©", "ru")
        self.assertNotIn("©", result, "RU: copyright should be stripped")

    def test_accept_valid_cjk(self):
        from miner.ocr import _filter_garbage

        self.assertEqual(_filter_garbage("你好世界", "zh"), "你好世界")
        self.assertEqual(_filter_garbage("こんにちは", "ja"), "こんにちは")
        self.assertEqual(_filter_garbage("안녕하세요", "ko"), "안녕하세요")

    def test_accept_valid_latin(self):
        from miner.ocr import _filter_garbage

        self.assertEqual(_filter_garbage("Quest completed", "en"), "Quest completed")
        self.assertEqual(_filter_garbage("Überprüfung", "de"), "Überprüfung")
        self.assertEqual(_filter_garbage("café", "fr"), "café")
        self.assertEqual(
            _filter_garbage("Zadanie ukończone", "pl"), "Zadanie ukończone"
        )

    def test_accept_valid_greek(self):
        from miner.ocr import _filter_garbage

        self.assertEqual(_filter_garbage("καλημέρα", "el"), "καλημέρα")

    def test_accept_valid_cyrillic(self):
        from miner.ocr import _filter_garbage

        self.assertEqual(_filter_garbage("привет", "ru"), "привет")

    def test_mixed_content_cjk(self):
        from miner.ocr import _filter_garbage

        result = _filter_garbage("你好world", "zh")
        cjk_count = len(
            re.findall(
                r"[\u4e00-\u9fff\u3040-\u309f\u30a0-\u30ff\uac00-\ud7af]", result
            )
        )
        non_cjk = len(result.replace(" ", "")) - cjk_count
        if cjk_count > 0:
            self.assertLessEqual(
                non_cjk,
                cjk_count * 0.4 + 1,
                "Mixed CJK with too much Latin should be filtered",
            )

    def test_mixed_content_latin(self):
        from miner.ocr import _filter_garbage

        result = _filter_garbage("Quest 12 completed", "en")
        self.assertNotIn("12", result, "Numbers should be stripped from Latin text")


class TestEdgeCases(unittest.TestCase):
    """Edge case tests."""

    def test_empty_image(self):
        from miner.ocr import ocr_image

        img = Image.new("L", (50, 50), 255)
        path = TEST_IMG_DIR / "empty.png"
        img.save(path)
        result = ocr_image(path, "en")
        self.assertIsInstance(result, str)

    def test_very_short_text(self):
        from miner.ocr import ocr_image

        for lang in LANGS:
            path = _create_test_image("A", fname=f"short_{lang}.png")
            result = ocr_image(path, lang)
            self.assertIsInstance(
                result, str, f"{lang}: short text should return string"
            )

    def test_very_long_text(self):
        from miner.ocr import ocr_image

        long_en = "The quick brown fox jumps over the lazy dog. " * 5
        path = _create_test_image(
            long_en, width=800, height=200, font_size=20, fname="long_en.png"
        )
        result = ocr_image(path, "en")
        self.assertGreater(len(result), 0, "Long text OCR should return something")

    def test_all_whitespace(self):
        from miner.text import is_valid_text

        self.assertFalse(is_valid_text("   "))
        self.assertFalse(is_valid_text("\t\n"))
        self.assertFalse(is_valid_text(""))

    def test_mixed_cjk_latin(self):
        from miner.text import clean_text

        result = clean_text("Hello 你好 World 世界")
        self.assertIn("Hello", result)
        self.assertIn("你好", result)

    def test_ocr_all_whitespace_image(self):
        from miner.ocr import ocr_image

        img = Image.new("L", (200, 50), 255)
        draw = ImageDraw.Draw(img)
        draw.text((10, 10), "     ", font=_get_font(24), fill=0)
        path = TEST_IMG_DIR / "whitespace.png"
        img.save(path)
        result = ocr_image(path, "en")
        self.assertIsInstance(result, str)

    def test_translation_empty_string(self):
        from miner.translate import translate_text

        self.assertIsNone(translate_text(""))
        self.assertIsNone(translate_text("   "))

    def test_translation_single_char(self):
        from miner.translate import translate_text

        result = translate_text("A", src="en", dest="en")
        self.assertIsNone(result)

    def test_text_validation_too_long(self):
        from miner.text import is_valid_text

        long_text = "A" * 600
        self.assertFalse(is_valid_text(long_text))

    def test_text_validation_copyright_only(self):
        from miner.text import is_valid_text

        self.assertFalse(is_valid_text("©"))
        self.assertFalse(is_valid_text("®"))
        self.assertFalse(is_valid_text("™"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
