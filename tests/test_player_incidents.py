"""Player archive incident badges must represent verified events, never guessed zeros."""
import json
import re
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
PAGE=(ROOT/"spillere.html").read_text(encoding="utf-8")

class PlayerIncidentTests(unittest.TestCase):
    def test_no_obsolete_transfermarkt_claims(self):
        self.assertNotIn("Transfermarkt", PAGE)
        self.assertIn("hvilke mål og kort vi har dokumenteret", PAGE)
        self.assertIn("det er ikke et nul", PAGE)

    def test_badges_and_detail_dialog_exist(self):
        self.assertIn('id="dialogEvents"', PAGE)
        self.assertIn("eventBadges(p)", PAGE)
        self.assertIn("dialogEvents.innerHTML=eventBadges(p)", PAGE)

    @unittest.skipUnless(shutil.which("node"), "Node.js required")
    def test_known_events_and_unknown_do_not_count_as_zero(self):
        # Exercise actual JavaScript, not mere presence of a function name.
        start=PAGE.index("const verifiedIncidents=")
        end=PAGE.index("const map=new Map(); raw.forEach",start)
        js=PAGE[start:end]
        cases=[
            {"name":"Tammy Abraham","seen":[{"match":"Roma 3–0 Lazio","name":"Tammy Abraham"}]},
            {"name":"Paletta","seen":[{"match":"AC Milan 1–4 Roma","name":"Paletta"}]},
            {"name":"Rasmus Højlund","seen":[{"match":"Napoli 2–1 Lecce","name":"Rasmus Højlund"}]},
            {"name":"Unknown","seen":[{"match":"Roma 3–0 Lazio","name":"Unknown"}]}
        ]
        script=js+"console.log(JSON.stringify("+json.dumps(cases,ensure_ascii=False)+".map(p=>({stats:observedEvents(p),markup:eventBadges(p)}))))"
        run=subprocess.run(["node","-e",script],capture_output=True,text=True,check=True)
        data=json.loads(run.stdout)
        self.assertEqual(data[0]["stats"],{"goals":2,"yellow":None,"red":None})
        self.assertEqual(data[1]["stats"],{"goals":None,"yellow":None,"red":1})
        self.assertEqual(data[2]["stats"]["goals"],1)
        self.assertEqual(data[3]["stats"],{"goals":None,"yellow":None,"red":None})
        self.assertIn("⚽ –",data[3]["markup"])
        self.assertIn("🟨 –",data[0]["markup"])
        self.assertIn("🟥 1",data[1]["markup"])

if __name__=="__main__":
    unittest.main()
