"""Behavioral checks for live league standings; read-only fixtures."""
import json, shutil, subprocess, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
SRC=(ROOT/"app/app.js").read_text(encoding="utf-8")
class LiveLeagueTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"),"Node.js required")
    def test_rules_and_scope(self):
        start=SRC.index("function leagueStatsFromSaved_(rows)")
        end=SRC.index("function paintLeagueAndGoals_(rows)",start)
        js="""const players={King:"King",Kardinalus:"Kardinalus",Pingvinus:"Pingvinus",Gorilla:"Gorilla",Kaninus:"Kaninus"};
function parseMoney(v){if(!v.trim())return null;var n=Number(v.replace(",", "."));return Number.isFinite(n)&&n>=0?n:null}
"""+SRC[start:end]
        rows=[
            {"week":43,"round":"Supercup","match":"Kardinalus – King","player":"Kardinalus","result":"3-1","money":"98,94"},
            {"week":44,"round":"Runde 1","match":"Kardinalus – Kaninus","player":"Kardinalus","result":"2-2","money":"30"},
            {"week":44,"round":"Runde 1","match":"Kardinalus – Kaninus","player":"Kaninus","result":"2-2","money":"10"},
            {"week":44,"round":"Runde 1","match":"Gorilla – King","player":"Gorilla","result":"0-0","money":"0"},
            {"week":44,"round":"Runde 1","match":"Gorilla – King","player":"King","result":"0-0","money":"0"},
            {"week":45,"round":"Runde 2","match":"Kardinalus – Pingvinus","player":"Kardinalus","result":"","money":""}
        ]
        proc=subprocess.run(["node","-e",js+"console.log(JSON.stringify(leagueStatsFromSaved_("+json.dumps(rows,ensure_ascii=False)+")))"],capture_output=True,text=True,check=True)
        data=json.loads(proc.stdout)
        league={x["name"]:x for x in data["league"]}
        self.assertEqual(league["Kardinalus"]["points"],3)
        self.assertEqual(league["Kaninus"]["points"],1)
        self.assertEqual(league["King"]["points"],1)
        self.assertEqual(league["Gorilla"]["points"],1)
        self.assertEqual(league["Pingvinus"]["played"],0)
        self.assertEqual(league["Kardinalus"]["forGoals"],2)
        self.assertEqual(data["goals"][0]["name"],"Kardinalus")
    def test_hero_card_updates_from_live_leader(self):
        start=SRC.index("function paintLeagueAndGoals_(rows)")
        end=SRC.index("function paintManagerFromSaved_(rows)",start)
        section=SRC[start:end]
        self.assertIn('card.querySelector(".leader-medal")',section)
        self.assertIn("name.textContent=players[leader.name]",section)
        self.assertIn('updated.textContent=played?',section)
        self.assertIn('detail.textContent=leader.points+',section)

    def test_reload_and_post_save_wiring(self):
        self.assertIn("paintLeagueAndGoals_(savedEntries);paintManagerFromSaved_",SRC)
        self.assertIn("paintLeagueAndGoals_(out.saved);paintManagerFromSaved_",SRC)
if __name__=="__main__":unittest.main()
