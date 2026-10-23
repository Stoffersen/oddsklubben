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

    def test_entry_drafts_autosave_and_clear_only_on_live_write(self):
        script=(ROOT/"app/app.js").read_text()
        self.assertIn('document.getElementById("cards").addEventListener("input"',script)
        self.assertIn('localStorage.setItem("oddsklubben-draft-"+data.week',script)
        self.assertIn('if(!restoreDraft_(x.w))restoreSaved_(x)',script)
        self.assertIn('if(out.status==="written"&&localStorage.getItem(',script)

    def test_completed_second_2026_season_is_listed(self):
        page=(ROOT/"index.html").read_text()
        self.assertIn('<small>2026 · 2</small><strong>🐧 Pingvinus</strong><b>1.702,50</b>',page)
        self.assertNotIn('2026 · 2</small><strong>⏳',page)

    def test_cache_versions_match(self):
        page=(ROOT/"index.html").read_text()
        worker=(ROOT/"sw.js").read_text()
        script=re.search(r'app/app\.js\?v=\d+',page)
        self.assertIsNotNone(script)
        self.assertIn(script.group(),worker)

if __name__=="__main__":
    unittest.main()
