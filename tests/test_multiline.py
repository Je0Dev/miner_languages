"""Tests for multiline buffer module."""
import sys, unittest, time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

class TestMultiline(unittest.TestCase):
    def test_add_and_get(self):
        from miner.multiline import MultiLineBuffer
        buf = MultiLineBuffer(max_lines=5, window_sec=10)
        buf.add("Line 1")
        buf.add("Line 2")
        buf.add("Line 3")
        self.assertEqual(len(buf.get_recent()), 3)
    
    def test_max_lines(self):
        from miner.multiline import MultiLineBuffer
        buf = MultiLineBuffer(max_lines=3, window_sec=10)
        for i in range(5):
            buf.add(f"Line {i}")
        self.assertLessEqual(len(buf.get_recent()), 3)
    
    def test_get_combined(self):
        from miner.multiline import MultiLineBuffer
        buf = MultiLineBuffer(max_lines=5, window_sec=10)
        buf.add("你好")
        buf.add("世界")
        combined = buf.get_combined()
        self.assertIn("你好", combined)
        self.assertIn("世界", combined)
    
    def test_get_all_text(self):
        from miner.multiline import MultiLineBuffer
        buf = MultiLineBuffer(max_lines=5, window_sec=10)
        buf.add("First")
        buf.add("Second")
        all_text = buf.get_all_text()
        self.assertIn("First", all_text)
        self.assertIn("Second", all_text)
    
    def test_clear(self):
        from miner.multiline import MultiLineBuffer
        buf = MultiLineBuffer(max_lines=5, window_sec=10)
        buf.add("Test")
        buf.clear()
        self.assertEqual(len(buf.get_recent()), 0)
    
    def test_empty_buffer(self):
        from miner.multiline import MultiLineBuffer
        buf = MultiLineBuffer(max_lines=5, window_sec=10)
        self.assertEqual(buf.get_combined(), "")
        self.assertEqual(buf.get_all_text(), "")

if __name__ == '__main__':
    unittest.main()
