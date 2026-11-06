import unittest
from pathlib import Path

HTML=(Path(__file__).resolve().parents[1]/"spillere.html").read_text(encoding="utf-8")

class PlayerArchiveNavigation(unittest.TestCase):
    def test_no_transfermarkt_links_or_filter(self):
        self.assertNotIn("transfermarkt.com",HTML)
        self.assertNotIn('id="dialogProfile"',HTML)
        self.assertNotIn('data-quick="profile"',HTML)
        self.assertNotIn("profiles[p.name]",HTML)

    def test_no_unverified_goal_or_card_stats(self):
        self.assertNotIn("const verifiedIncidents=",HTML)
        self.assertNotIn("eventBadges(p)",HTML)
        self.assertNotIn('id="dialogEvents"',HTML)
        self.assertNotIn('class="event-coverage"',HTML)
        self.assertIn("Se hvilke kampe de spillede, og hvor mange gange vi har set dem.",HTML)

    def test_player_details_still_present(self):
        self.assertIn('id="playerDialog"',HTML)
        self.assertIn('data-quick="multi"',HTML)
        self.assertIn('id="clubFilter"',HTML)

if __name__=="__main__":
    unittest.main()
