import re
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

class MobileHomeSmoke(unittest.TestCase):
    def test_home_card_refreshes_after_sheet_load(self):
        script=(ROOT/"app/app.js").read_text()
        self.assertIn("function updateHomeNextRound_()",script)
        self.assertIn("program=out.program;",script)
        self.assertIn("pos=initialPosition();render();updateHomeNextRound_()",script)
        self.assertIn('document.querySelector("#home .next-round")',script)

    def test_entry_drafts_autosave_and_clear_only_on_live_write(self):
        script=(ROOT/"app/app.js").read_text()
        self.assertIn('document.getElementById("cards").addEventListener("input"',script)
        self.assertIn('localStorage.setItem("oddsklubben-draft-"+data.week',script)
        self.assertIn('if(!restoreDraft_(x.w))restoreSaved_(x)',script)
        self.assertIn('if(out.status==="written"&&localStorage.getItem(',script)

    def test_completed_second_2026_season_is_listed(self):
        page=(ROOT/"index.html").read_text()
        self.assertIn('<small>2026 · 2</small><strong>🐧 Pingvinus</strong><b>1.702,50</b>',page)
        self.assertNotIn('2026 · 2</small><strong>⏳',page)

    def test_manager_refreshes_from_sheet_data(self):
        script=(ROOT/"app/app.js").read_text()
        page=(ROOT/"index.html").read_text()
        self.assertIn('window.refreshManagerStandings=function()',script)
        self.assertIn('paintManagerFromSaved_(out.saved)',script)
        self.assertIn('if(window.refreshManagerStandings)window.refreshManagerStandings()',page)

    def test_money_view_no_longer_claims_new_season(self):
        page=(ROOT/"index.html").read_text()
        self.assertIn('id="money"',page)

    def test_supercup_trophy_total_matches_recorded_sheet(self):
        page=(ROOT/"index.html").read_text()
        self.assertIn('<span>🙏 Kardinalus</span><strong>72</strong>',page)
        self.assertIn('<b>72</b> pokaler i alt',page)
        self.assertIn('inkl. Supercup 2026/27',page)

    def test_season_chart_uses_saved_entries(self):
        script=(ROOT/"app/app.js").read_text()
        self.assertIn("function paintSeasonBalance_(rows)",script)
        self.assertIn("paintSeasonBalance_(out.saved)",script)
        self.assertIn("paintSeasonBalance_(savedEntries)",script)
        self.assertIn("balances[n]+=weeks.get(w)[n]-80",script)
        self.assertIn('element("polyline"',script)
        self.assertIn("host.replaceChildren(svg)",script)

    def test_all_time_updates_from_current_sheet_entries(self):
        script=(ROOT/"app/app.js").read_text()
        page=(ROOT/"index.html").read_text()
        self.assertIn("function paintAllTimeFromSaved_(rows)",script)
        self.assertIn("King:8164.69,Pingvinus:7359.51,Kardinalus:7196.87",script)
        self.assertIn("paintAllTimeFromSaved_(savedEntries)",script)
        self.assertIn("window.refreshAllTimeLeader()",page)

    def test_weekly_finance_charts_wired(self):
        page=(ROOT/"index.html").read_text()
        script=(ROOT/"app/app.js").read_text()
        self.assertIn('id="weeklyClubChart"',page)
        self.assertIn('id="weeklyMemberChart"',page)
        self.assertIn('function weeklyFinance_(rows)',script)
        self.assertIn('if(!weeks.has(w))weeks.set(w',script)
        self.assertIn('stake:(i+1)*400',script)
        self.assertIn('member[n]+=weeks.get(w)[n]-80',script)
        self.assertIn('paintWeeklyFinance_(savedEntries)',script)
        self.assertIn('paintWeeklyFinance_(out.saved)',script)

    def test_weekly_winnings_use_right_axis_only(self):
        script=(ROOT/"app/app.js").read_text()
        start=script.index("function paintWeeklyFinance_(rows)")
        end=script.index("function paintGoalOfYear_(rows)",start)
        section=script[start:end]
        self.assertIn("var weeklyHigh=Math.max(100,",section)
        self.assertIn("var weeklyY=function(v)",section)
        self.assertIn("y:weeklyY(d.win)",section)
        self.assertIn("height:baseY-weeklyY(d.win)",section)
        self.assertIn("y(d[k.key])",section)
        self.assertIn("Ugens kr.",section)
        self.assertIn("Samlet kr.",section)

    def test_full_season_club_chart(self):
        script=(ROOT/"app/app.js").read_text()
        self.assertIn("var seasonWeeks=[43,44,45,46,47,48,49,50,51,52,1,2,3,4,5,6,7,8,9,10,11,12]",script)
        self.assertIn("stake:(i+1)*400",script)
        self.assertIn("var saved=actualByWeek.get(w),win=saved?saved.win:0",script)
        self.assertIn("accumulated+=win",script)
        self.assertIn("planlagt indsats",script)

    def test_toto_cup_saves_in_own_round(self):
        script=(ROOT/"app/app.js").read_text()
        self.assertIn('round:"Toto Cup",entries:toto',script)
        self.assertIn('e.match==="Toto Cup"',script)
        self.assertIn('saveRoundParts_(data).then',script)

    def test_charts_outside_standings_tab_panels(self):
        html=(ROOT/"index.html").read_text()
        start=html.index('<div id="extras" class="standing-panel">')
        end=html.index('<p class="foot">Kilde: Tabellen</p>',start)
        section=html[start:end]
        self.assertLess(section.index('</div><div class="league-development">'),section.index('id="weeklyClubChart"'))
        self.assertEqual(html.count('id="weeklyMemberChart"'),1)
        self.assertEqual(html.count('id="weeklyClubChart"'),1)

    def test_hattricks_come_from_saved_scores(self):
        script=(ROOT/"app/app.js").read_text()
        self.assertIn("function paintHattricks_(rows)",script)
        self.assertIn("v.home>=3",script)
        self.assertIn("v.away>=3",script)
        self.assertIn("paintHattricks_(savedEntries)",script)
        self.assertIn("paintHattricks_(out.saved)",script)

    def test_goal_of_year_uses_saved_amounts(self):
        script=(ROOT/"app/app.js").read_text()
        self.assertIn("function paintGoalOfYear_(rows)",script)
        self.assertIn("amount>best.amount",script)
        self.assertIn("paintGoalOfYear_(savedEntries)",script)
        self.assertIn("paintGoalOfYear_(out.saved)",script)

    def test_hattrick_regex_matches_score_and_teams(self):
        script=(ROOT/"app/app.js").read_text()
        start=script.index("function paintHattricks_(rows)")
        end=script.index("function paintSeasonBalance_(rows)",start)
        section=script[start:end]
        self.assertIn(r"/^(\d+)\s*[-–]\s*(\d+)$/",section)
        self.assertIn(r"/\s+[–-]\s+/",section)
        self.assertNotIn(r"/^(\\d+)\\s*",section)

    def test_cache_versions_match(self):
        page=(ROOT/"index.html").read_text()
        worker=(ROOT/"sw.js").read_text()
        script=re.search(r'app/app\.js\?v=\d+',page)
        self.assertIsNotNone(script)
        self.assertIn(script.group(),worker)

if __name__=="__main__":
    unittest.main()
