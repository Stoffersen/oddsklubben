import unittest
from pathlib import Path

HTML=(Path(__file__).resolve().parents[1]/"spillere.html").read_text(encoding="utf-8")

class PlayerArchiveNavigation(unittest.TestCase):
    def test_no_transfermarkt_links_or_filter(self):
        self.assertNotIn("transfermarkt.com",HTML)
        self.assertNotIn('id="dialogProfile"',HTML)
        self.assertNotIn('data-quick="profile"',HTML)
        self.assertNotIn("profiles[p.name]",HTML)

    def test_player_details_still_present(self):
        self.assertIn('id="playerDialog"',HTML)
        self.assertIn('data-quick="multi"',HTML)
        self.assertIn('id="clubFilter"',HTML)

if __name__=="__main__":
    unittest.main()
