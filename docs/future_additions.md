# Future Additions - Sentence Mining Improvements

## Overview
Planned improvements to the sentence mining workflow for better language learning outcomes, with a focus on Chinese and multi-language support.

## 1. Sentence Splitting in Mining Pipeline
- Integrate `split_sentences()` from `text.py` into `mine.mine_sentence()` and `overlay.LiveOCROverlay._mine()`
- When OCR captures multiple sentences, automatically split them into separate entries
- Each sentence gets its own entry in `sentences.json`, its own Anki card, etc.
- Configurable toggle: split vs. keep-as-block

## 2. Editable Text Preview in Overlay
- Replace the read-only `Text` widget with an editable one
- After each live OCR capture, user can edit the text before clicking "Mine"
- Add a "Split Preview" button showing how it'll break into individual cards
- Add "Discard" button to skip bad captures

## 3. Duplicate Detection in Pipeline
- Use `is_duplicate_smart()` from `duplicates.py` in both `mine.py` and `overlay.py`
- Check before saving; show duplicate warning in overlay with "Skip / Save Anyway"
- Handle OCR variations (Levenshtein-based comparison)

## 4. Chinese Word Segmentation + Per-Word Lookups
- Add `jieba` for Chinese word segmentation
- Per-word display: word -> pinyin -> dictionary definition (via `cc-cedict`)
- Show breakdown in overlay's pronunciation area
- Store word breakdown in `sentences.json` (new `words` field)
- Export to Anki as additional "Word Breakdown" field
- Modular design: Japanese `mecab`/`unidic` and Korean `konlpy`/`mecab-ko` later

## 5. Tagging & Context
- Add "Tags" field (list of strings) and "Character" field to entries
- In overlay: small tag input + character name input
- Auto-suggest tags: "dialogue", "narration", "quest", "item", "system"
- Preserve game context for better review

## 6. Enhanced Web Viewer
- Show word-by-word breakdown on each card
- Filter by tags / language / source / character
- Bulk tag/edit/delete sentences
- Quick filtered Anki export
- Study mode: show sentence, hide translation

## 7. Audio Quality
- Improve VAD trim with noise gate
- Audio cleanup before saving

## Implementation Priority

| # | Feature | Effort | Benefit |
|---|---------|--------|---------|
| 1 | Sentence splitting in mining pipeline | ~1hr | Huge |
| 2 | Editable text preview in overlay | ~2hr | Huge |
| 3 | Duplicate detection in pipeline | ~1hr | Medium |
| 4 | Chinese word segmentation + word details | ~3hr | Huge for learning |
| 5 | Tagging & context | ~2hr | Medium |
| 6 | Enhanced web viewer | ~2hr | Medium |
| 7 | Audio quality improvements | ~1hr | Low |
