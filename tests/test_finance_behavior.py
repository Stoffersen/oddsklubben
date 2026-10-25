"""Behavioral regression tests for Oddsklubben finance and awards, no Sheet writes."""
import json
import shutil
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = (ROOT / "app/app.js").read_text(encoding="utf-8")


def section(start, end):
    return SCRIPT[SCRIPT.index(start):SCRIPT.index(end, SCRIPT.index(start))]


JS = "\n".join([
    section("function parseMoney(", "function validResult("),
    section("function weeklyFinance_(", "function weeklyFinanceSvg_("),
    section("function paintGoalOfYear_(", "function paintHattricks_("),
    section("function paintHattricks_(", "function paintSeasonBalance_("),
])


@unittest.skipUnless(shutil.which("node"), "Node.js required for behavioral JavaScript checks")
class FinanceBehavior(unittest.TestCase):
    def evaluate(self, body):
        runtime = """
const players={Pingvinus:"🐧 Pingvinus",King:"👑 King",Gorilla:"🦍 Gorilla",Kaninus:"🐰 Kaninus",Kardinalus:"🙏 Kardinalus"};
const labels={};
const panel={
 querySelectorAll:()=>["Hattrick","Årets Mål"].map(name=>({
   textContent:name,querySelector:()=>({
     set textContent(v){labels[name]=v}
   })
 }))
};
const document={getElementById:()=>panel};
"""
        run = subprocess.run(["node", "-e", runtime + JS + "\n" + body],
                             capture_output=True, text=True, cwd=ROOT, check=True)
        return json.loads(run.stdout)

    def test_week_43_two_competitions_only_one_stake(self):
        rows = [
            dict(week=43,round="Supercup",match="Kardinalus – King",player="Kardinalus",money="98,94",result="3-1"),
            dict(week=43,round="Supercup",match="Kardinalus – King",player="King",money="57,15",result="3-1")
        ] + [dict(week=43,round="Toto Cup",match="Toto Cup",player=n,money="0",result="")
                           for n in ("Pingvinus","Gorilla","Kaninus")]
        result = self.evaluate("const rows=" + json.dumps(rows, ensure_ascii=False) +
                               ";console.log(JSON.stringify(weeklyFinance_(rows)))")
        self.assertEqual(len(result["series"]), 1)
        self.assertAlmostEqual(result["series"][0]["win"], 156.09)
        self.assertEqual(result["series"][0]["stake"], 400)
        self.assertAlmostEqual(result["total"], -243.91)
        self.assertEqual(len(result["members"]), 5)

    def test_future_template_rows_do_not_create_paid_weeks(self):
        rows = [dict(week=43,player="Pingvinus",money="0",result=""),
                dict(week=44,player="King",money="",result=""),
                dict(week=45,player="King",money="",result="")]
        out = self.evaluate("console.log(JSON.stringify(weeklyFinance_(" +
                            json.dumps(rows) + ")))")
        self.assertEqual([x["week"] for x in out["series"]], [43])
        self.assertEqual(out["total"], -400)

    def test_supercup_hattrick_deduplicated_and_awards_update(self):
        rows = [
            dict(week=43,round="Supercup",match="Kardinalus – King",player="Kardinalus",money="98,94",result="3-1"),
            dict(week=43,round="Supercup",match="Kardinalus – King",player="King",money="57,15",result="3-1")
        ]
        code = ("const rows=" + json.dumps(rows, ensure_ascii=False) +
                ";paintHattricks_(rows);paintGoalOfYear_(rows);console.log(JSON.stringify(labels))")
        result = self.evaluate(code)
        self.assertIn("Kardinalus 1", result["Hattrick"])
        self.assertTrue(result["Hattrick"].startswith("1"))
        self.assertIn("98,94", result["Årets Mål"])

    def test_new_highest_winning_takes_lead(self):
        rows = [dict(week=43,player="Kardinalus",money="98,94"),
                dict(week=44,player="Kaninus",money="125,50")]
        out = self.evaluate("paintGoalOfYear_(" + json.dumps(rows) +
                            ");console.log(JSON.stringify(labels))")
        self.assertIn("Kaninus", out["Årets Mål"])
        self.assertIn("125,50", out["Årets Mål"])


if __name__ == "__main__":
    unittest.main()
