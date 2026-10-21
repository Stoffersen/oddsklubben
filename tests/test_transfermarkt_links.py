import re
import unittest
from pathlib import Path

HTML=(Path(__file__).resolve().parents[1]/"spillere.html").read_text(encoding="utf-8")

class TransfermarktLinks(unittest.TestCase):
    def test_links_use_regular_navigation(self):
        self.assertIn('id="dialogProfile" rel="noopener"',HTML)
        self.assertIn('href="\'+profile+\'" rel="noopener"',HTML)
        self.assertNotIn('target="_blank" rel="noopener"',HTML)

    def test_profiles_use_explicit_https_urls(self):
        urls=re.findall(r'https://www\\.transfermarkt\\.com/[^"]+',HTML)
        self.assertGreater(len(urls),100)
        self.assertTrue(all("/spieler/" in url for url in urls))

if __name__=="__main__":
    unittest.main()
