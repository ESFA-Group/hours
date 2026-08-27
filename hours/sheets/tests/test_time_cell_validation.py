import copy

from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient

from sheets.models import Sheet, User, coerce_time_cell


class CoerceTimeCellTests(TestCase):
    """Unit table for the write-path canonicalizer.

    Decimal input is read as decimal hours: "0.5" is half an hour. The old client
    normalizer instead produced the string "0.5:00", which the jspreadsheet hh:mm
    mask rendered back as "05:00" while the server scored it as 0 minutes.
    """

    def test_decimal_hours_are_converted(self):
        self.assertEqual(coerce_time_cell('0.5'), '00:30')
        self.assertEqual(coerce_time_cell('0.5:00'), '00:30')
        self.assertEqual(coerce_time_cell('3.5:00'), '03:30')
        self.assertEqual(coerce_time_cell('2.25'), '02:15')
        self.assertEqual(coerce_time_cell('  3.5  '), '03:30')

    def test_plain_values_are_canonicalized(self):
        self.assertEqual(coerce_time_cell('8'), '08:00')
        self.assertEqual(coerce_time_cell('08:00'), '08:00')
        self.assertEqual(coerce_time_cell('10:30'), '10:30')
        self.assertEqual(coerce_time_cell('16:'), '16:00')
        self.assertEqual(coerce_time_cell('0'), '00:00')
        self.assertEqual(coerce_time_cell('00'), '00:00')

    def test_blank_and_legacy_int_zero_become_zero(self):
        # 255 live cells in production hold the JSON int 0 rather than "00:00".
        # These must coerce, never reject, or their owners cannot save at all.
        self.assertEqual(coerce_time_cell(0), '00:00')
        self.assertEqual(coerce_time_cell(''), '00:00')
        self.assertEqual(coerce_time_cell(None), '00:00')
        self.assertEqual(coerce_time_cell('   '), '00:00')

    def test_persian_digits(self):
        self.assertEqual(coerce_time_cell('۵:۳۰'), '05:30')

    def test_invalid_values_are_rejected(self):
        for value in ('1.5:45', '-1:30', '8:75', 'abc', '1000:00', '8:30:00', 5, True):
            self.assertIsNone(coerce_time_cell(value), msg=repr(value))


class SheetTimeCellApiTests(TestCase):
    """The save endpoint must canonicalize duration cells before storing them."""

    def setUp(self):
        self.client = APIClient()
        self.user = self._make_user('worker')
        self.year, self.month = 1403, 1
        self.sheet = Sheet.objects.create(
            user=self.user,
            user_name=self.user.get_full_name(),
            year=self.year,
            month=self.month,
        )
        self.sheet.data = Sheet.empty_sheet_data(self.year, self.month)
        for row in self.sheet.data:
            row.update(
                {
                    'Auto Hours': '00:00',
                    'Rest': '00:00',
                    'Remote': '00:00',
                    'Mission': '00:00',
                    'Forget': '00:00',
                }
            )
        self.sheet.save()
        self.client.force_authenticate(self.user)

    def _make_user(self, username, **kwargs):
        defaults = {
            'password': 'pass',
            'first_name': username,
            'last_name': 'User',
            'first_name_p': username,
            'last_name_p': 'User',
            'email': f'{username}@example.com',
            'national_ID': '1234567890',
            'dob': '1360/01/01',
            'mobile1': '09120000000',
            'address': 'Address',
            'emergency_phone': '09120000001',
            'bank_name': 'Bank',
            'card_number': '1234567890123456',
            'account_number': '1234567890123',
            'SHEBA_number': 'IR123456789012345678901234',
            'personal_image': 'p.jpg',
            'national_ID_front_image': 'f.jpg',
            'national_ID_back_image': 'b.jpg',
            'birth_cert_first_page': 'bc1.jpg',
            'birth_cert_changes_page': 'bc2.jpg',
        }
        defaults.update(kwargs)
        return User.objects.create_user(username=username, **defaults)

    def _url(self):
        return reverse(
            'sheets:api_sheets', kwargs={'year': self.year, 'month': self.month}
        )

    def _post(self, payload):
        return self.client.post(self._url(), payload, format='json')

    def test_decimal_rest_is_stored_as_hh_mm(self):
        """Regression for the reported bug (Soheil Safavi, 1405/5 day 5).

        Rest "0.5:00" used to store verbatim and score 0 minutes server-side, so
        Total was the untouched Forget value.
        """
        grid = copy.deepcopy(self.sheet.data)
        grid[4].update({'Rest': '0.5:00', 'Forget': '10:30'})

        response = self._post({'saveSheet': True, 'data': grid})
        self.assertEqual(response.status_code, 200)

        self.sheet.refresh_from_db()
        self.assertEqual(self.sheet.data[4]['Rest'], '00:30')
        self.assertEqual(self.sheet.data[4]['Total'], '10:00')

    def test_bare_decimal_rest_is_stored_as_hh_mm(self):
        grid = copy.deepcopy(self.sheet.data)
        grid[4].update({'Rest': '3.5', 'Auto Hours': '08:00'})

        response = self._post({'saveSheet': True, 'data': grid})
        self.assertEqual(response.status_code, 200)

        self.sheet.refresh_from_db()
        self.assertEqual(self.sheet.data[4]['Rest'], '03:30')
        self.assertEqual(self.sheet.data[4]['Total'], '04:30')

    def test_legacy_int_zero_and_free_text_note_are_accepted(self):
        """Guard against an over-strict validator.

        255 live cells hold the int 0, some Total cells hold "-1:30", and Note
        Hours legitimately holds Persian sentences. None of these may 400.
        """
        grid = copy.deepcopy(self.sheet.data)
        note = 'ورود رو باید 00:00 میزدم'
        grid[4].update({'Rest': 0, 'Total': '-1:30', 'Note Hours': note})

        response = self._post({'saveSheet': True, 'data': grid})
        self.assertEqual(response.status_code, 200)

        self.sheet.refresh_from_db()
        self.assertEqual(self.sheet.data[4]['Rest'], '00:00')
        self.assertEqual(self.sheet.data[4]['Note Hours'], note)

    def test_uncoercible_value_is_rejected_and_grid_untouched(self):
        before = copy.deepcopy(self.sheet.data)
        grid = copy.deepcopy(self.sheet.data)
        grid[4]['Rest'] = 'abc'

        response = self._post({'saveSheet': True, 'data': grid})
        self.assertEqual(response.status_code, 400)
        self.assertIn('Rest', response.data['error'])
        self.assertIn('5', response.data['error'])
        self.assertEqual(response.data['invalidCells'][0]['column'], 'Rest')
        self.assertEqual(response.data['invalidCells'][0]['day'], 5)

        self.sheet.refresh_from_db()
        self.assertEqual(self.sheet.data, before)


class RepairTimeCellsCommandTests(TestCase):
    """The repair command fixes stored cells and recomputes the aggregates."""

    def setUp(self):
        self.user = User.objects.create_user(
            username='soheil',
            password='pass',
            first_name='Soheil',
            last_name='Safavi',
            first_name_p='Soheil',
            last_name_p='Safavi',
            email='soheil@example.com',
            national_ID='1234567890',
            dob='1360/01/01',
            mobile1='09120000000',
            address='Address',
            emergency_phone='09120000001',
            bank_name='Bank',
            card_number='1234567890123456',
            account_number='1234567890123',
            SHEBA_number='IR123456789012345678901234',
            personal_image='p.jpg',
            national_ID_front_image='f.jpg',
            national_ID_back_image='b.jpg',
            birth_cert_first_page='bc1.jpg',
            birth_cert_changes_page='bc2.jpg',
        )
        self.sheet = Sheet.objects.create(
            user=self.user,
            user_name=self.user.get_full_name(),
            year=1403,
            month=1,
        )
        data = Sheet.empty_sheet_data(1403, 1)
        for row in data:
            row.update(
                {
                    'Auto Hours': '00:00',
                    'Rest': '00:00',
                    'Remote': '00:00',
                    'Mission': '00:00',
                    'Forget': '00:00',
                }
            )
        # Mirrors sheet 3362: a corrupt Rest plus a legacy int-0 Forget.
        data[4].update({'Rest': '0.5:00', 'Forget': '10:30'})
        data[18].update({'Rest': '3.5:00', 'Forget': 0, 'Auto Hours': '15:54'})
        Sheet.objects.filter(pk=self.sheet.pk).update(data=data)

    def test_command_repairs_cells_and_totals(self):
        call_command('repair_time_cells', sheet=[self.sheet.pk], verbosity=0)

        self.sheet.refresh_from_db()
        self.assertEqual(self.sheet.data[4]['Rest'], '00:30')
        self.assertEqual(self.sheet.data[4]['Total'], '10:00')
        self.assertEqual(self.sheet.data[18]['Rest'], '03:30')
        self.assertEqual(self.sheet.data[18]['Forget'], '00:00')
        self.assertEqual(self.sheet.data[18]['Total'], '12:24')
        # 10:00 + 12:24 in minutes
        self.assertEqual(self.sheet.total, 600 + 744)

    def test_dry_run_writes_nothing(self):
        call_command(
            'repair_time_cells', sheet=[self.sheet.pk], dry_run=True, verbosity=0
        )

        self.sheet.refresh_from_db()
        self.assertEqual(self.sheet.data[4]['Rest'], '0.5:00')

    def test_uncoercible_cell_is_skipped_unless_set(self):
        self.sheet.refresh_from_db()
        data = copy.deepcopy(self.sheet.data)
        data[6]['Rest'] = 'abc'
        Sheet.objects.filter(pk=self.sheet.pk).update(data=data)

        call_command('repair_time_cells', sheet=[self.sheet.pk], verbosity=0)
        self.sheet.refresh_from_db()
        self.assertEqual(self.sheet.data[6]['Rest'], 'abc')

        call_command(
            'repair_time_cells',
            sheet=[self.sheet.pk],
            overrides=[f'{self.sheet.pk}:7:Rest=01:15'],
            verbosity=0,
        )
        self.sheet.refresh_from_db()
        self.assertEqual(self.sheet.data[6]['Rest'], '01:15')
