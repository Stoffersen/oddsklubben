"""Behavior regression: the app trophy matrix mirrors the club trophy archive."""
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class TableReader(HTMLParser):
    def __init__(self, marker):
        super().__init__()
        self.marker = marker
        self.in_table = False
        self.in_cell = False
        self.rows = []
        self.row = None
        self.cell = None
        self.champion = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "table" and (not self.marker or self.marker in attrs.get("class", "")):
            self.in_table = True
        elif self.in_table and tag == "tr":
            self.row = []
        elif self.in_table and self.row is not None and tag in ("th", "td"):
            self.cell = []
            self.in_cell = True
            self.champion = "champ" in attrs.get("class", "").split()

    def handle_data(self, data):
        if self.in_cell:
            self.cell.append(data)

    def handle_endtag(self, tag):
        if self.in_table and tag in ("td", "th") and self.in_cell:
            self.row.append((" ".join("".join(self.cell).split()), self.champion))
            self.in_cell = False
        elif self.in_table and tag == "tr" and self.row is not None:
            self.rows.append(self.row)
            self.row = None
        elif self.in_table and tag == "table":
            self.in_table = False


def read_table(filename, marker):
    parser = TableReader(marker)
    parser.feed((ROOT / filename).read_text(encoding="utf-8"))
    return parser.rows


class TrophyMatrixTests(unittest.TestCase):
    def test_all_categories_counts_and_reigning_champions_match_archive(self):
        website = read_table("pokaler.html", "")
        mobile = read_table("index.html", "mobile-trophy-matrix")
        self.assertEqual(len(website), 17)  # heading, 15 categories, totals
        self.assertEqual(len(mobile), len(website))
        for original, app in zip(website[1:], mobile[1:]):
            self.assertEqual(app, original)
        champions = [champ for row in mobile[1:-1] for _, champ in row]
        self.assertEqual(sum(champions), 15)
        self.assertTrue(all(sum(champ for _, champ in row) == 1 for row in mobile[1:-1]))
        self.assertEqual([value for value, _ in mobile[-1]], [
            "Pokaler Total", "72", "31", "44", "14", "41", "9", "4", "5"
        ])

    def test_mobile_trophy_table_is_inside_trophy_view_not_a_website_link(self):
        page = (ROOT / "index.html").read_text(encoding="utf-8")
        trophy_view = page.split('<main id="trophies"', 1)[1].split('<main id="standings"', 1)[0]
        self.assertLess(trophy_view.index('class="podium-cards"'), trophy_view.index('class="mobile-trophy-archive"'))
        self.assertLess(trophy_view.index('class="mobile-trophy-archive"'), trophy_view.index('class="section-head records-head"'))
        self.assertNotIn('All-time stilling', trophy_view)
        self.assertNotIn('<section class="ranking">', trophy_view)
        self.assertLess(trophy_view.index('class="mobile-trophy-archive"'), trophy_view.index('id="backTrophiesBottom"'))
        self.assertIn('class="mobile-trophy-scroll" role="region"', trophy_view)
        self.assertIn('tabindex="0"', trophy_view)
        self.assertNotIn('href="pokaler.html"', trophy_view)
        self.assertIn('Gul = regerende mester', trophy_view)
        self.assertIn('aria-label="Regerende mester:', trophy_view)

    def test_scroll_sticky_category_and_pwa_assets_versioned(self):
        css = (ROOT / "app/styles.css").read_text(encoding="utf-8")
        page = (ROOT / "index.html").read_text(encoding="utf-8")
        sw = (ROOT / "sw.js").read_text(encoding="utf-8")
        self.assertRegex(css, r"\.mobile-trophy-scroll\{[^}]*overflow-x:auto")
        self.assertRegex(css, r"\.mobile-trophy-matrix th:first-child\{[^}]*position:sticky")
        self.assertIn("app/styles.css?v=20261122-bot-retired", page)
        self.assertIn("app/styles.css?v=20261122-bot-retired", sw)
        self.assertIn("oddsklubben-shell-v117", sw)


if __name__ == "__main__":
    unittest.main()
