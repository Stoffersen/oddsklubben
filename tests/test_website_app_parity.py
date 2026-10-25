import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class WebsiteAppParity(unittest.TestCase):
    def test_trophy_totals_follow_app(self):
        app=(ROOT/"index.html").read_text(encoding="utf-8")
        web=(ROOT/"pokaler.html").read_text(encoding="utf-8")
        stats=(ROOT/"stats.html").read_text(encoding="utf-8")
        self.assertIn("🙏 Kardinalus · 72",web)
        self.assertIn("<th>Pokaler Total</th><td class=\"best\">72</td>",web)
        self.assertIn("<th>Super Cup</th><td class=\"champ\">13</td>",web)
        self.assertIn("<b>201</b><span>registrerede pokaler",web)
        self.assertIn("<strong>🙏 Kardinalus</strong><span><b>72</b> pokaler i alt",app)
        self.assertIn("201 aktive spillerpokaler",stats)
        self.assertNotIn("Kardinalus · 71",web)

    def test_manager_fetch_uses_live_saved_data_and_safe_dom(self):
        web=(ROOT/"stats.html").read_text(encoding="utf-8")
        self.assertIn('id="manager-bars"',web)
        self.assertIn("Array.isArray(data.saved)",web)
        self.assertIn("stats-site/live-season.js",web)
        self.assertIn('id="website-alltime-bars"',web)
        self.assertIn('id="website-goal-of-year"',web)

if __name__=="__main__":
    unittest.main()
