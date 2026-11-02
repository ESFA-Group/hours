import pandas as pd
from django.test import SimpleTestCase

from sheets.api_views import MonthlyReportApiView as M


class ReportRoundingTests(SimpleTestCase):
    def test_half_split_adds_up_to_total(self):
        row = M.round_row(pd.Series({"Total": 13239.0, "A": 6619.5, "B": 6619.5}))
        self.assertEqual(row["A"] + row["B"], row["Total"])

    def test_float_noise_rounds_up(self):
        row = M.round_row(
            pd.Series({"Total": 8989.0, "A": 5393.999999999999, "B": 3595.0000000001})
        )
        self.assertEqual((row["A"], row["B"]), (5394, 3595))

    def test_three_way_split_adds_up(self):
        row = M.round_row(pd.Series({"Total": 100.0, "A": 100 / 3, "B": 100 / 3, "C": 100 / 3, "D": 0.0}))
        self.assertEqual(row[["A", "B", "C", "D"]].sum(), 100)
        self.assertEqual(row["D"], 0)

    def test_decimal_percent_is_parsed(self):
        from sheets.models import Sheet
        parse = Sheet().parse_project_porp
        self.assertEqual((parse("80.00 %"), parse("100"), parse("")), (0.8, 1.0, 0))
