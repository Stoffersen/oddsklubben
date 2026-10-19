import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class MobileHomeSmoke(unittest.TestCase):
    def test_home_card_refreshes_after_sheet_load(self):
        script=(ROOT/"app/app.js").read_text()
        self.assertIn("function updateHomeNextRound_()",script)
        self.assertIn("program=out.program;",script)
        self.assertIn("pos=initialPosition();render();updateHomeNextRound_()",script)
        self.assertIn('document.querySelector("#home .next-round")',script)

    def test_cache_versions_match(self):
        page=(ROOT/"index.html").read_text()
        worker=(ROOT/"sw.js").read_text()
        script=re.search(r'app/app\.js\?v=\d+',page)
        self.assertIsNotNone(script)
        self.assertIn(script.group(),worker)

if __name__=="__main__":
    unittest.main()
