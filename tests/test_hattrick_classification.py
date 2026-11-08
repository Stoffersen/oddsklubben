"""Three goals are a hattrick; four or more are Saksespark, not both."""
import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SRC=(ROOT/"app/app.js").read_text(encoding="utf-8")

class HattrickClassificationTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which("node"),"Node.js required")
    def test_four_goal_game_is_not_a_hattrick(self):
        start=SRC.index("function paintHattricks_(rows)")
        end=SRC.index("function paintSeasonBalance_(rows)",start)
        script=SRC[start:end]
        rows=[
            {"week":43,"round":"Supercup","match":"Kardinalus – King","result":"3-1"},
            {"week":45,"round":"Runde 2","match":"Kaninus – Gorilla","result":"0-4"},
            {"week":45,"round":"Runde 2","match":"Kaninus – Gorilla","result":"0-4"}
        ]
        preface="""
const players={Kardinalus:"🙏 Kardinalus",King:"👑 King",Gorilla:"🦍 Gorilla",Kaninus:"🐰 Kaninus",Pingvinus:"🐧 Pingvinus"};
const strong={textContent:""};
const row={textContent:"3️⃣ Hattrick",querySelector:()=>strong};
const document={getElementById:()=>({querySelectorAll:()=>[row]})};
"""
        js=preface+script+"paintHattricks_("+json.dumps(rows,ensure_ascii=False)+");console.log(JSON.stringify(strong.textContent));"
        result=subprocess.run(["node","-e",js],check=True,capture_output=True,text=True)
        self.assertEqual(json.loads(result.stdout),"1 · 🙏 Kardinalus 1")

if __name__=="__main__":unittest.main()
