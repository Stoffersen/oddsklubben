import copy
import json
import unittest
from pathlib import Path
from src.bot_compatible_feed import build_compatible_feed

class CompatibleFeedTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.legacy=json.loads((Path(__file__).resolve().parents[1]/"data/bot-bets.json").read_text())

    def test_empty_new_data_is_identical_and_nonmutating(self):
        before=copy.deepcopy(self.legacy)
        self.assertEqual(build_compatible_feed(self.legacy,[]),before)
        self.assertEqual(self.legacy,before)
        self.assertTrue(any(w.get("excluded_from_totals") for w in before["weeks"]))

    def test_additive_settled_coupon_preserves_legacy(self):
        week={"coupon_id":"new-coupon","coupon_date":"2026-10-25","status":"settled",
              "stake_kr":20,"return_kr":30,"profit_kr":10,
              "bets":[{"bet_id":"new-bet","stake_kr":20,"return_kr":30}]}
        output=build_compatible_feed(self.legacy,[week])
        self.assertEqual(output["weeks"][:len(self.legacy["weeks"])],self.legacy["weeks"])
        self.assertEqual(output["totals"]["stake_kr"],180)
        self.assertEqual(output["totals"]["return_kr"],269.2)
        self.assertEqual(output["totals"]["profit_kr"],89.2)
        self.assertEqual(output["totals"]["settled_weeks"],3)
        self.assertEqual(self.legacy["totals"]["profit_kr"],79.2)

    def test_duplicate_or_fabricated_identity_fails(self):
        week={"coupon_id":"new-coupon","coupon_date":"2026-10-25","status":"settled",
              "stake_kr":20,"return_kr":30,"profit_kr":10,
              "bets":[{"bet_id":"new-bet","stake_kr":20,"return_kr":30}]}
        with self.assertRaises(ValueError):
            build_compatible_feed(self.legacy,[week,week])
        with self.assertRaises(ValueError):
            build_compatible_feed(self.legacy,[dict(week,coupon_date="2026-10-18")])
        with self.assertRaises(ValueError):
            build_compatible_feed(self.legacy,[dict(week,coupon_id="")])

    def test_bad_legacy_totals_block_projection(self):
        legacy=copy.deepcopy(self.legacy)
        legacy["totals"]["profit_kr"]=999
        with self.assertRaises(ValueError):
            build_compatible_feed(legacy,[])
