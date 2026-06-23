import copy
from datetime import time
from tempfile import NamedTemporaryFile

import pandas as pd
from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from tablib import Dataset

from sheets.admin import UserResource
from sheets.models import Sheet, User


class HourApprovalWorkflowTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.employee = self._user('employee', auto_hour_ID=100)
        self.manager_1 = self._user('manager1', is_HourVerifier=True)
        self.manager_2 = self._user('manager2', is_HourVerifier=True)
        self.supreme = self._user('supreme', is_SupremeHourVerifier=True)
        self.other = self._user('other', is_HourVerifier=True)

        self.employee.manager_level_1 = self.manager_1
        self.employee.manager_level_2 = self.manager_2
        self.employee.save()

        self.sheet = Sheet.objects.create(user=self.employee, user_name=self.employee.get_full_name(), year=1403, month=1)
        self.sheet.data = [
            {
                'Day': 1,
                'WeekDay': 'Sat',
                'Attendance': '',
                'Auto Hours': '08:00',
                'Rest': '00:30',
                'Remote': '00:00',
                'Total': '07:30',
                'Note Hours': '',
                'Description': '',
            }
        ]
        self.sheet.save()

    def _user(self, username, **kwargs):
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
        user = User.objects.create_user(username=username, **defaults)
        return user

    def _submit_sheet(self):
        self.client.force_authenticate(self.employee)
        url = reverse('sheets:api_sheets', kwargs={'year': 1403, 'month': 1})
        response = self.client.put(url, {'submit': True}, format='json')
        self.assertEqual(response.status_code, 200)
        self.sheet.refresh_from_db()

    def _verify_url(self):
        return reverse('sheets:api_verify_hours', kwargs={'year': 1403, 'month': 1})

    def test_user_can_submit_sheet(self):
        self._submit_sheet()
        self.assertTrue(self.sheet.submitted)

    def test_user_cannot_unsubmit_or_resubmit_after_submission(self):
        self._submit_sheet()
        response = self.client.put(reverse('sheets:api_sheets', kwargs={'year': 1403, 'month': 1}), {'submit': True}, format='json')
        self.assertEqual(response.status_code, 409)
        self.sheet.refresh_from_db()
        self.assertTrue(self.sheet.submitted)

    def test_manager_level_1_can_verify_assigned_employee(self):
        self._submit_sheet()
        self.client.force_authenticate(self.manager_1)
        response = self.client.post(self._verify_url(), {'userId': self.employee.id, 'action': 'verify_manager_level_1'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.sheet.refresh_from_db()
        self.assertTrue(self.sheet.manager_level_1_verified)

    def test_manager_level_1_cannot_verify_unrelated_employee(self):
        self._submit_sheet()
        self.client.force_authenticate(self.other)
        response = self.client.post(self._verify_url(), {'userId': self.employee.id, 'action': 'verify_manager_level_1'}, format='json')
        self.assertEqual(response.status_code, 403)

    def test_manager_level_1_cannot_reject_after_manager_level_2_approval(self):
        self._submit_sheet()
        self.sheet.manager_level_1_verified = True
        self.sheet.manager_level_2_verified = True
        self.sheet.save()
        self.client.force_authenticate(self.manager_1)
        response = self.client.post(self._verify_url(), {'userId': self.employee.id, 'action': 'reject_manager_level_1'}, format='json')
        self.assertEqual(response.status_code, 403)

    def test_manager_level_2_can_verify_assigned_employee(self):
        self._submit_sheet()
        self.sheet.manager_level_1_verified = True
        self.sheet.save()
        self.client.force_authenticate(self.manager_2)
        response = self.client.post(self._verify_url(), {'userId': self.employee.id, 'action': 'verify_manager_level_2'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.sheet.refresh_from_db()
        self.assertTrue(self.sheet.manager_level_2_verified)

    def test_manager_level_2_cannot_reject_after_supreme_approval(self):
        self._submit_sheet()
        self.sheet.manager_level_1_verified = True
        self.sheet.manager_level_2_verified = True
        self.sheet.supreme_verified = True
        self.sheet.save()
        self.client.force_authenticate(self.manager_2)
        response = self.client.post(self._verify_url(), {'userId': self.employee.id, 'action': 'reject_manager_level_2'}, format='json')
        self.assertEqual(response.status_code, 403)

    def test_supreme_can_verify_submitted_sheet(self):
        self._submit_sheet()
        self.client.force_authenticate(self.supreme)
        response = self.client.post(self._verify_url(), {'userId': self.employee.id, 'action': 'verify_supreme'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.sheet.refresh_from_db()
        self.assertTrue(self.sheet.supreme_verified)

    def test_supreme_can_reject_submitted_sheet(self):
        self._submit_sheet()
        self.client.force_authenticate(self.supreme)
        response = self.client.post(self._verify_url(), {'userId': self.employee.id, 'action': 'reject_supreme', 'reason': 'اصلاح شود'}, format='json')
        self.assertEqual(response.status_code, 200)
        self.sheet.refresh_from_db()
        self.assertFalse(self.sheet.submitted)
        self.assertEqual(self.sheet.rejection_reason, 'اصلاح شود')

    def test_nobody_can_verify_or_reject_unsubmitted_sheets(self):
        self.client.force_authenticate(self.manager_1)
        response = self.client.post(self._verify_url(), {'userId': self.employee.id, 'action': 'verify_manager_level_1'}, format='json')
        self.assertEqual(response.status_code, 400)

    def test_attendance_import_skips_submitted_sheets(self):
        self._submit_sheet()
        df = pd.DataFrame([{
            'کد پرسنلي': 100,
            'کد در دستگاه': 100,
            'نام': 'Employee',
            'نام خانوادگي': 'User',
            'تاريخ': '1403/01/01',
            'مدت حضور': time(9, 0),
            **{f'ورود {i}': 0 for i in range(1, 6)},
            **{f'خروج {i}': 0 for i in range(1, 6)},
        }])
        with NamedTemporaryFile(suffix='.xlsx') as tmp:
            df.to_excel(tmp.name, index=False)
            call_command('import_hours', tmp.name, '1403', '1')
        self.sheet.refresh_from_db()
        self.assertEqual(self.sheet.data[0]['Auto Hours'], '08:00')

    def test_user_import_export_supports_manager_usernames(self):
        resource = UserResource()
        dataset = Dataset(
            headers=['username', 'first_name_p', 'last_name_p', 'staff_group_tag', 'auto_hour_ID', 'manager_level_1', 'manager_level_2', 'payment_type']
        )
        dataset.append(['new_employee', 'New', 'User', 1, 200, 'manager1', 'manager2', 'hours'])
        result = resource.import_data(dataset, dry_run=False, raise_errors=True)
        self.assertFalse(result.has_errors())
        user = User.objects.get(username='new_employee')
        self.assertEqual(user.manager_level_1, self.manager_1)
        self.assertEqual(user.manager_level_2, self.manager_2)

    def test_verify_page_sections_return_correct_employees(self):
        self._submit_sheet()
        self.client.force_authenticate(self.manager_1)
        response = self.client.get(self._verify_url())
        self.assertEqual(response.status_code, 200)
        current_ids = [item['userId'] for item in response.data['sections']['currentQueue']]
        self.assertIn(self.employee.id, current_ids)

    def test_user_hours_api_shows_status_flags(self):
        self._submit_sheet()
        self.sheet.manager_level_1_verified = True
        self.sheet.save()
        self.client.force_authenticate(self.employee)
        response = self.client.get(reverse('sheets:api_sheets', kwargs={'year': 1403, 'month': 1}))
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.data['submitted'])
        self.assertTrue(response.data['manager_level_1_verified'])
        self.assertFalse(response.data['manager_level_2_verified'])


class SheetEmptyProtectionTests(TestCase):
    """Guards the hours grid against being wiped by empty/partial saves
    (dropped connection, incomplete page load, client bugs) while keeping
    legitimate edits -- including adding a project to a blank sheet -- working.
    """

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
        # A realistic full-month grid with real hours logged on day 1.
        self.sheet.data = Sheet.empty_sheet_data(self.year, self.month)
        self.sheet.data[0].update(
            {'Auto Hours': '08:00', 'Rest': '00:00', 'Remote': '00:00'}
        )
        self.sheet.save()
        self.full_rows = len(self.sheet.data)
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

    # --- protection against accidental emptying ---

    def test_empty_data_is_rejected_and_sheet_preserved(self):
        response = self._post({'saveSheet': True, 'data': []})
        self.assertEqual(response.status_code, 400)
        self.sheet.refresh_from_db()
        self.assertEqual(len(self.sheet.data), self.full_rows)
        self.assertEqual(self.sheet.data[0]['Auto Hours'], '08:00')

    def test_missing_data_is_rejected_and_sheet_preserved(self):
        response = self._post({'saveSheet': True})
        self.assertEqual(response.status_code, 400)
        self.sheet.refresh_from_db()
        self.assertEqual(len(self.sheet.data), self.full_rows)
        self.assertEqual(self.sheet.data[0]['Auto Hours'], '08:00')

    def test_partial_data_is_rejected_and_sheet_preserved(self):
        partial = copy.deepcopy(self.sheet.data)[:5]
        response = self._post({'saveSheet': True, 'data': partial})
        self.assertEqual(response.status_code, 400)
        self.sheet.refresh_from_db()
        self.assertEqual(len(self.sheet.data), self.full_rows)
        self.assertEqual(self.sheet.data[0]['Auto Hours'], '08:00')

    # --- legitimate flows still work ---

    def test_full_grid_saves(self):
        full = copy.deepcopy(self.sheet.data)
        full[1].update({'Auto Hours': '07:00'})
        response = self._post({'saveSheet': True, 'data': full})
        self.assertEqual(response.status_code, 200)
        self.sheet.refresh_from_db()
        self.assertEqual(len(self.sheet.data), self.full_rows)
        self.assertEqual(self.sheet.data[1]['Auto Hours'], '07:00')

    def test_adding_project_to_blank_sheet_saves(self):
        # Simulate a blank sheet (no hours yet) plus the "add project" action,
        # which sends the full grid with a new project column.
        blank = Sheet.empty_sheet_data(self.year, self.month)
        for row in blank:
            row.update(
                {'Auto Hours': '00:00', 'Rest': '00:00', 'Remote': '00:00', 'ProjectX': ''}
            )
        blank[0].update({'Auto Hours': '08:00', 'ProjectX': '100'})
        response = self._post({'saveSheet': True, 'data': blank})
        self.assertEqual(response.status_code, 200)
        self.sheet.refresh_from_db()
        self.assertEqual(len(self.sheet.data), self.full_rows)
        self.assertEqual(self.sheet.data[0]['ProjectX'], '100')

    # --- editSheet hardening ---

    def test_editsheet_cannot_blank_data(self):
        response = self._post(
            {'editSheet': True, 'field': 'data', 'row': {'userID': self.user.id, 'data': []}}
        )
        self.assertEqual(response.status_code, 400)
        self.sheet.refresh_from_db()
        self.assertEqual(len(self.sheet.data), self.full_rows)

    def test_editsheet_allows_payment_fields(self):
        response = self._post(
            {
                'editSheet': True,
                'field': 'reduction1',
                'row': {'userID': self.user.id, 'reduction1': 12345},
            }
        )
        self.assertEqual(response.status_code, 200)
        self.sheet.refresh_from_db()
        self.assertEqual(self.sheet.reduction1, 12345)

    # --- self-heal on read ---

    def test_get_heals_empty_sheet(self):
        Sheet.objects.filter(pk=self.sheet.pk).update(data=[])
        response = self.client.get(self._url())
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']), self.full_rows)
