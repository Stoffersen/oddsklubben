"""Golden Cage leader must show the player and use the club tie-breaks."""
import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=(ROOT/"app/app.js").read_text(encoding="utf-8")

class GoldenCageTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"),"Node.js required")
    def test_leader_from_registered_matches(self):
        a=SRC.index("function leagueStatsFromSaved_(rows)")
        b=SRC.index("function goldenCageStandings_(rows)",a)
        c=SRC.index("function goldenCageStandings_(rows)")
        d=SRC.index("function paintGoldenCage_(rows)",c)
        js='const players={King:"King",Kardinalus:"Kardinalus",Pingvinus:"Pingvinus",Gorilla:"Gorilla",Kaninus:"Kaninus"};\n'
        js+='function parseMoney(x){const n=Number(String(x).replace(",","."));return Number.isFinite(n)?n:null}\n'
        js+=SRC[a:b]+SRC[c:d]
        rows=[
            {"week":44,"round":"Runde 1","match":"Kardinalus – Kaninus","player":"Kardinalus","result":"0-0","money":"0"},
            {"week":44,"round":"Runde 1","match":"Kardinalus – Kaninus","player":"Kaninus","result":"0-0","money":"0"},
            {"week":44,"round":"Runde 1","match":"Gorilla – King","player":"Gorilla","result":"3-2","money":"116,5"},
            {"week":44,"round":"Runde 1","match":"Gorilla – King","player":"King","result":"3-2","money":"179,4"},
            {"week":45,"round":"Runde 2","match":"Kardinalus – Pingvinus","player":"Kardinalus","result":"3-0","money":"120,49"},
            {"week":45,"round":"Runde 2","match":"Kardinalus – Pingvinus","player":"Pingvinus","result":"3-0","money":"0"},
            {"week":45,"round":"Runde 2","match":"Kaninus – Gorilla","player":"Kaninus","result":"0-4","money":"0"},
            {"week":45,"round":"Runde 2","match":"Kaninus – Gorilla","player":"Gorilla","result":"0-4","money":"151"},
            {"week":46,"round":"Runde 3","match":"King – Pingvinus","player":"King","result":"","money":""},
            {"week":43,"round":"Supercup","match":"Kardinalus – King","player":"Kardinalus","result":"3-1","money":"98,94"}
        ]
        cmd=js+"console.log(JSON.stringify(goldenCageStandings_("+json.dumps(rows,ensure_ascii=False)+")));"
        result=subprocess.run(["node","-e",cmd],check=True,capture_output=True,text=True)
        data=json.loads(result.stdout)
        self.assertEqual(data[0]["name"],"Kardinalus")
        self.assertEqual(data[0]["against"],0)
        self.assertEqual(data[0]["played"],2)
        self.assertEqual({x["name"]:x["against"] for x in data},
                         {"Kardinalus":0,"Gorilla":2,"King":3,"Pingvinus":3,"Kaninus":4})
        self.assertEqual(data[0]["winnings"],120.49)

    def test_refresh_paths_and_label(self):
        self.assertIn("paintGoldenCage_(savedEntries);",SRC)
        self.assertIn("paintGoldenCage_(out.saved);",SRC)
        self.assertIn('players[p.name]',SRC)
        self.assertIn('first.against+" imod"',SRC)

if __name__=="__main__":
    unittest.main()
