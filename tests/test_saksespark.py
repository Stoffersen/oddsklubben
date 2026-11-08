"""Saksespark is a four-goal match, counted once per match and player."""
import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=(ROOT/"app/app.js").read_text(encoding="utf-8")

class SaksesparkTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"),"Node.js required")
    def test_four_goals_away_and_home_with_no_double_count(self):
        start=SRC.index("function saksesparkStats_(rows)")
        end=SRC.index("function paintSaksespark_(rows)",start)
        js='const players={King:"King",Kardinalus:"Kardinalus",Pingvinus:"Pingvinus",Gorilla:"Gorilla",Kaninus:"Kaninus"};\n'+SRC[start:end]
        rows=[
          {"week":45,"round":"Runde 2","match":"Kaninus – Gorilla","player":"Kaninus","result":"0-4"},
          {"week":45,"round":"Runde 2","match":"Kaninus – Gorilla","player":"Gorilla","result":"0-4"},
          {"week":44,"round":"Runde 1","match":"Gorilla – King","result":"3-2"},
          {"week":43,"round":"Supercup","match":"Kardinalus – King","result":"3-1"},
          {"week":46,"round":"Runde 3","match":"King – Pingvinus","result":""},
          {"week":47,"round":"Runde 4","match":"Pingvinus – King","result":"5-0"},
          {"week":48,"round":"Runde 5","match":"King – Kardinalus","result":"4-0"},
        ]
        result=subprocess.run(["node","-e",js+"console.log(JSON.stringify(saksesparkStats_("+json.dumps(rows,ensure_ascii=False)+")));"],capture_output=True,text=True,check=True)
        counts=json.loads(result.stdout)
        self.assertEqual(counts,{"King":1,"Kardinalus":0,"Pingvinus":1,"Gorilla":1,"Kaninus":0})

    def test_reload_and_refresh_paths(self):
        self.assertIn("paintHattricks_(savedEntries);paintSaksespark_(savedEntries);",SRC)
        self.assertIn("paintHattricks_(out.saved);paintSaksespark_(out.saved);",SRC)
        self.assertIn('row.querySelector("strong").textContent=String(total)',SRC)

if __name__=="__main__":unittest.main()
