from django.test import SimpleTestCase

from sheets.models import Sheet


def _row(auto="00:00", remote="00:00", mission="00:00", forget="00:00", rest="00:00", **extra):
    return {
        "Auto Hours": auto, "Remote": remote, "Mission": mission,
        "Forget": forget, "Rest": rest, **extra,
    }


class RestHoursTests(SimpleTestCase):
    """Rest only offsets time worked that day. rowMinutes() in hours.html and
    calculateRowTotalMinutes() in verify_hour_panel.js implement the same rule."""

    def setUp(self):
        self.sheet = Sheet(year=1405, month=7)

    def test_rest_on_day_with_nothing_worked_has_no_effect(self):
        mins = self.sheet.row_minutes(_row(rest="01:00"))
        self.assertEqual(mins["Rest"], 0)
        self.assertEqual(mins["Total"], 0)

    def test_rest_is_deducted_from_any_worked_column(self):
        for col in ("auto", "remote", "mission", "forget"):
            mins = self.sheet.row_minutes(_row(rest="01:00", **{col: "08:00"}))
            self.assertEqual(mins["Rest"], 60, col)
            self.assertEqual(mins["Total"], 7 * 60, col)

    def test_rest_is_capped_at_time_worked(self):
        mins = self.sheet.row_minutes(_row(auto="00:30", rest="02:00"))
        self.assertEqual(mins["Rest"], 30)
        self.assertEqual(mins["Total"], 0)

    def test_breakdown_always_adds_up_to_total(self):
        rows = [
            _row(rest="03:00"),
            _row(auto="08:00", rest="00:30"),
            _row(remote="01:00", mission="02:00", forget="00:15", rest="05:00"),
            _row(auto="04:00", remote="04:00"),
        ]
        for row in rows:
            m = self.sheet.row_minutes(row)
            self.assertEqual(
                m["Auto Hours"] + m["Remote"] + m["Mission"] + m["Forget"] - m["Rest"],
                m["Total"],
            )

    def test_transform_matches_row_minutes(self):
        self.sheet.data = [
            _row(rest="03:00"),
            _row(auto="08:00", rest="00:30"),
            _row(auto="00:30", rest="02:00"),
            _row(remote="04:00", mission="01:00"),
        ]
        df = self.sheet.transform()
        self.assertEqual(
            list(df["Hours"]),
            [self.sheet.row_minutes(r)["Total"] for r in self.sheet.data],
        )

    def test_legacy_manual_hours_survive_rest_only_day(self):
        # Submitted legacy sheets keep their manual Hours on days with nothing
        # worked; a stray Rest must not wipe them out.
        self.sheet.submitted = True
        self.sheet.data = [
            _row(rest="01:00", Hours="06:00"),
            _row(auto="08:00", rest="01:00", Hours="06:00"),
        ]
        self.assertEqual(list(self.sheet.transform()["Hours"]), [6 * 60, 7 * 60])
