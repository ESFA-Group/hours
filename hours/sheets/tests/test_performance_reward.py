from django.core.exceptions import ValidationError
from django.test import TestCase, override_settings
from django.urls import reverse
from rest_framework.test import APIClient

from sheets.models import Sheet, User


# Page tests render {% static %}; skip the collectstatic manifest.
PLAIN_STATIC = {
    "default": {"BACKEND": "django.core.files.storage.FileSystemStorage"},
    "staticfiles": {"BACKEND": "django.contrib.staticfiles.storage.StaticFilesStorage"},
}


class PerformanceRewardTestBase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.employee = self._user('employee', auto_hour_ID=100, wage=100_000, reward_base=20_000_000)
        self.manager_1 = self._user('manager1', is_HourVerifier=True)
        self.manager_2 = self._user('manager2', is_HourVerifier=True)
        self.supreme = self._user('supreme', is_SupremeHourVerifier=True)
        self.other = self._user('other', is_HourVerifier=True)
        self.payment_manager = self._user('payer', is_PaymentManager=True)
        self.superuser = self._user('root', is_PaymentManager=True, is_superuser=True, is_staff=True)

        self.employee.manager_level_1 = self.manager_1
        self.employee.manager_level_2 = self.manager_2
        self.employee.save()

        self.sheet = self._sheet(self.employee, 1)

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
        return User.objects.create_user(username=username, **defaults)

    def _sheet(self, user, month):
        sheet = Sheet.objects.create(user=user, year=1403, month=month)
        sheet.setup_sheet()
        sheet.data = [
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
        sheet.save()
        return sheet

    def _verify_url(self):
        return reverse('sheets:api_verify_hours', kwargs={'year': 1403, 'month': 1})

    def _post_perf(self, actor, mode, **data):
        self.client.force_authenticate(actor)
        payload = {'userId': self.employee.id, 'action': 'save_comments', 'mode': mode, **data}
        return self.client.post(f'{self._verify_url()}?mode={mode}', payload, format='json')

    def _detail(self, actor, mode):
        self.client.force_authenticate(actor)
        return self.client.get(self._verify_url(), {'mode': mode, 'userId': self.employee.id})


class RewardCalculationTests(PerformanceRewardTestBase):
    def _set_m2(self, value):
        self.sheet.performance_form_aspect_m2 = value
        self.sheet.save()
        self.sheet.refresh_from_db()
        return self.sheet.addition_3_reward

    def test_normal_percentage(self):
        self.assertEqual(self._set_m2(85), 17_000_000)

    def test_minimum_and_maximum_percentage(self):
        self.assertEqual(self._set_m2(1), 200_000)
        self.assertEqual(self._set_m2(100), 20_000_000)

    def test_unset_m2_gives_no_reward(self):
        self.assertEqual(self._set_m2(None), 0)

    def test_m1_does_not_affect_reward(self):
        self._set_m2(50)
        self.sheet.performance_form_aspect_m1 = 100
        self.sheet.save()
        self.sheet.refresh_from_db()
        self.assertEqual(self.sheet.addition_3_reward, 10_000_000)

    def test_model_validation_rejects_out_of_range(self):
        for bad in (0, 101):
            for field in ('performance_form_aspect_m1', 'performance_form_aspect_m2'):
                setattr(self.sheet, field, bad)
                with self.assertRaises(ValidationError):
                    self.sheet.full_clean()
                setattr(self.sheet, field, None)

    def test_recalculates_when_reward_base_changes(self):
        self._set_m2(85)
        self.sheet.reward_base = 10_000_000
        self.sheet.save()
        self.sheet.refresh_from_db()
        self.assertEqual(self.sheet.addition_3_reward, 8_500_000)

    def test_recalculates_on_partial_save(self):
        self._set_m2(85)
        self.sheet.performance_form_aspect_m2 = 50
        self.sheet.save(update_fields=['performance_form_aspect_m2'])
        self.sheet.refresh_from_db()
        self.assertEqual(self.sheet.addition_3_reward, 10_000_000)

        self.sheet.reward_base = 4_000_000
        self.sheet.save(update_fields=['reward_base'])
        self.sheet.refresh_from_db()
        self.assertEqual(self.sheet.addition_3_reward, 2_000_000)

    def test_reward_is_added_to_final_payment_but_not_to_total(self):
        total_before = self.sheet.get_total_payment()
        final_before = self.sheet.get_final_payment()
        self._set_m2(85)
        self.assertEqual(self.sheet.get_total_payment(), total_before)
        self.assertEqual(self.sheet.get_final_payment(), final_before + 17_000_000)
        self.assertEqual(
            self.sheet.get_complementary_payment(),
            self.sheet.get_final_payment() - self.sheet.base_payment,
        )

    def test_new_sheet_snapshots_user_reward_base(self):
        self.assertEqual(self.sheet.reward_base, 20_000_000)

    def test_default_sheet_works_everywhere(self):
        plain = self._user('plain')
        sheet = Sheet.objects.create(user=plain, year=1403, month=1)
        sheet.setup_sheet()
        info = sheet.get_payment_info()
        self.assertEqual(info['rewardBase'], 0)
        self.assertIsNone(info['performanceM1'])
        self.assertIsNone(info['performanceM2'])
        self.assertEqual(info['addition3Reward'], 0)


class PerformancePermissionTests(PerformanceRewardTestBase):
    def _reload(self):
        self.sheet.refresh_from_db()
        return self.sheet

    def test_m1_can_edit_m1_but_not_m2(self):
        self.assertEqual(self._post_perf(self.manager_1, 'manager', performanceM1=70).status_code, 200)
        self.assertEqual(self._reload().performance_form_aspect_m1, 70)
        response = self._post_perf(self.manager_1, 'manager', performanceM2=70)
        self.assertEqual(response.status_code, 403)
        self.assertIsNone(self._reload().performance_form_aspect_m2)

    def test_m2_can_edit_m2_but_not_m1(self):
        response = self._post_perf(self.manager_2, 'manager', performanceM2=85)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['addition3Reward'], 17_000_000)
        self.assertEqual(self._reload().addition_3_reward, 17_000_000)
        self.assertEqual(self._post_perf(self.manager_2, 'manager', performanceM1=85).status_code, 403)
        self.assertIsNone(self._reload().performance_form_aspect_m1)

    def test_m1_cannot_overwrite_m2_in_a_combined_request(self):
        self.sheet.performance_form_aspect_m2 = 90
        self.sheet.save()
        response = self._post_perf(self.manager_1, 'manager', performanceM1=60, performanceM2=10)
        self.assertEqual(response.status_code, 403)
        sheet = self._reload()
        self.assertIsNone(sheet.performance_form_aspect_m1)
        self.assertEqual(sheet.performance_form_aspect_m2, 90)

    def test_supreme_can_edit_each_independently(self):
        self.assertEqual(self._post_perf(self.supreme, 'supreme', performanceM1=40).status_code, 200)
        self.assertEqual(self._reload().performance_form_aspect_m1, 40)
        self.assertIsNone(self.sheet.performance_form_aspect_m2)

        self.assertEqual(self._post_perf(self.supreme, 'supreme', performanceM2=55).status_code, 200)
        sheet = self._reload()
        self.assertEqual(sheet.performance_form_aspect_m1, 40)
        self.assertEqual(sheet.performance_form_aspect_m2, 55)
        self.assertEqual(sheet.addition_3_reward, 11_000_000)

    def test_supreme_needs_the_supreme_panel(self):
        # Not an assigned manager, so the manager panel refuses them.
        response = self._post_perf(self.supreme, 'manager', performanceM2=55)
        self.assertEqual(response.status_code, 403)
        self.assertIsNone(self._reload().performance_form_aspect_m2)

    def test_unrelated_verifier_cannot_edit(self):
        for key in ('performanceM1', 'performanceM2'):
            self.assertEqual(self._post_perf(self.other, 'manager', **{key: 50}).status_code, 403)
            self.assertEqual(self._post_perf(self.other, 'supreme', **{key: 50}).status_code, 403)
        sheet = self._reload()
        self.assertIsNone(sheet.performance_form_aspect_m1)
        self.assertIsNone(sheet.performance_form_aspect_m2)

    def test_managers_cannot_use_the_supreme_panel(self):
        self.assertEqual(self._post_perf(self.manager_2, 'supreme', performanceM2=50).status_code, 403)

    def test_legacy_group_verifier_can_comment_but_not_rate(self):
        self.employee.manager_level_1 = None
        self.employee.staff_group_tag = 7
        self.employee.save()
        legacy = self._user('legacy', is_HourVerifier=True, verifier_group_tags='7')

        detail = self._detail(legacy, 'manager')
        self.assertEqual(detail.status_code, 200)
        self.assertTrue(detail.data['permissions']['canEditManagerLevel1Comment'])
        self.assertFalse(detail.data['permissions']['canEditPerformanceM1'])
        self.assertFalse(detail.data['permissions']['canEditPerformanceM2'])

        ok = self._post_perf(legacy, 'manager', managerLevel1Comment='looks fine')
        self.assertEqual(ok.status_code, 200)
        self.assertEqual(self._post_perf(legacy, 'manager', performanceM1=80).status_code, 403)
        self.assertIsNone(self._reload().performance_form_aspect_m1)

    def test_permission_flags_in_detail(self):
        cases = [
            (self.manager_1, 'manager', True, False),
            (self.manager_2, 'manager', False, True),
            (self.supreme, 'supreme', True, True),
        ]
        for actor, mode, m1, m2 in cases:
            perms = self._detail(actor, mode).data['permissions']
            self.assertEqual(perms['canEditPerformanceM1'], m1, actor.username)
            self.assertEqual(perms['canEditPerformanceM2'], m2, actor.username)

    def test_invalid_values_rejected_without_changes(self):
        self.sheet.performance_form_aspect_m2 = 85
        self.sheet.save()
        for bad in (0, 101, -5, 'abc', '85.5', 85.5, True, [], {}):
            response = self._post_perf(self.manager_2, 'manager', performanceM2=bad)
            self.assertEqual(response.status_code, 400, bad)
            sheet = self._reload()
            self.assertEqual(sheet.performance_form_aspect_m2, 85)
            self.assertEqual(sheet.addition_3_reward, 17_000_000)

    def test_boundaries_and_numeric_strings_accepted(self):
        for value, expected in ((1, 1), (100, 100), ('42', 42)):
            self.assertEqual(self._post_perf(self.manager_2, 'manager', performanceM2=value).status_code, 200)
            self.assertEqual(self._reload().performance_form_aspect_m2, expected)

    def test_blank_clears_rating(self):
        self._post_perf(self.manager_2, 'manager', performanceM2=85)
        self.assertEqual(self._post_perf(self.manager_2, 'manager', performanceM2=None).status_code, 200)
        sheet = self._reload()
        self.assertIsNone(sheet.performance_form_aspect_m2)
        self.assertEqual(sheet.addition_3_reward, 0)

    def test_rating_bundled_with_verify_persists_and_rejection_keeps_it(self):
        self.client.force_authenticate(self.employee)
        self.client.put(reverse('sheets:api_sheets', kwargs={'year': 1403, 'month': 1}), {'submit': True}, format='json')
        self.client.force_authenticate(self.manager_1)
        response = self.client.post(self._verify_url(), {
            'userId': self.employee.id, 'action': 'verify_manager_level_1', 'performanceM1': 77,
        }, format='json')
        self.assertEqual(response.status_code, 200)
        sheet = self._reload()
        self.assertTrue(sheet.manager_level_1_verified)
        self.assertEqual(sheet.performance_form_aspect_m1, 77)

        self.client.force_authenticate(self.manager_2)
        self.client.post(self._verify_url(), {
            'userId': self.employee.id, 'action': 'reject_manager_level_2', 'reason': 'fix',
        }, format='json')
        sheet = self._reload()
        self.assertFalse(sheet.submitted)
        self.assertEqual(sheet.performance_form_aspect_m1, 77)


class FinancialDisplayTests(PerformanceRewardTestBase):
    def test_detail_returns_six_values_in_both_panels(self):
        self.sheet.performance_form_aspect_m1 = 60
        self.sheet.performance_form_aspect_m2 = 85
        self.sheet.save()
        for actor, mode in ((self.manager_1, 'manager'), (self.supreme, 'supreme')):
            data = self._detail(actor, mode).data
            self.assertEqual(data['wage'], 100_000)
            self.assertEqual(data['totalPayment'], self.sheet.get_total_payment())
            self.assertEqual(data['totalPayment'], 7.5 * 100_000)  # 07:30 worked, not 450 minutes
            self.assertEqual(data['rewardBase'], 20_000_000)
            self.assertEqual(data['performanceM1'], 60)
            self.assertEqual(data['performanceM2'], 85)
            self.assertEqual(data['addition3Reward'], 17_000_000)

    def test_employee_sheet_api_hides_ratings(self):
        self.client.force_authenticate(self.employee)
        data = self.client.get(reverse('sheets:api_sheets', kwargs={'year': 1403, 'month': 1})).data
        self.assertNotIn('performance_form_aspect_m1', data)
        self.assertNotIn('performance_form_aspect_m2', data)

    def test_employee_payment_box_shows_reward_and_m2_only(self):
        self.sheet.performance_form_aspect_m1 = 60
        self.sheet.performance_form_aspect_m2 = 85
        self.sheet.save()
        self.client.force_authenticate(self.employee)
        data = self.client.get(reverse('sheets:api_public_payment', kwargs={'year': 1403, 'month': 1})).data
        self.assertEqual(data['addition3Reward'], 17_000_000)
        self.assertEqual(data['performanceM2'], 85)
        self.assertNotIn('performanceM1', data)
        self.assertEqual(data['complementaryPayment'], self.sheet.get_complementary_payment())


class PaymentRewardTests(PerformanceRewardTestBase):
    def _payment_url(self, month=1):
        return reverse('sheets:api_payment', kwargs={'year': 1403, 'month': month})

    def _row(self, actor):
        self.client.force_authenticate(actor)
        rows = self.client.get(self._payment_url()).data
        return next(r for r in rows if r['userID'] == self.employee.id)

    def test_payment_api_returns_reward_fields(self):
        self.sheet.performance_form_aspect_m2 = 85
        self.sheet.save()
        row = self._row(self.payment_manager)
        self.assertEqual(row['rewardBase'], 20_000_000)
        self.assertIsNone(row['performanceM1'])
        self.assertEqual(row['performanceM2'], 85)
        self.assertEqual(row['addition3Reward'], 17_000_000)
        self.assertEqual(row['finalPayment'], self.sheet.get_final_payment())

    def test_superuser_updates_reward_base_forward(self):
        later = self._sheet(self.employee, 3)
        self.sheet.performance_form_aspect_m2 = 50
        self.sheet.save()
        row = self._row(self.superuser)
        row['rewardBase'] = 30_000_000
        response = self.client.post(self._payment_url(), {'row': row}, format='json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['addition3Reward'], 15_000_000)
        self.employee.refresh_from_db()
        later.refresh_from_db()
        self.assertEqual(self.employee.reward_base, 30_000_000)
        self.assertEqual(later.reward_base, 30_000_000)

    def test_payment_manager_cannot_change_reward_base(self):
        row = self._row(self.payment_manager)
        row['rewardBase'] = 1
        response = self.client.post(self._payment_url(), {'row': row}, format='json')
        self.assertEqual(response.status_code, 200)
        self.employee.refresh_from_db()
        self.sheet.refresh_from_db()
        self.assertEqual(self.employee.reward_base, 20_000_000)
        self.assertEqual(self.sheet.reward_base, 20_000_000)

    def test_malformed_reward_base_rejected(self):
        row = self._row(self.superuser)
        row['rewardBase'] = 'lots'
        response = self.client.post(self._payment_url(), {'row': row}, format='json')
        self.assertEqual(response.status_code, 400)
        self.employee.refresh_from_db()
        self.assertEqual(self.employee.reward_base, 20_000_000)


@override_settings(STORAGES=PLAIN_STATIC)
class PageRenderTests(PerformanceRewardTestBase):
    def test_payment_page_columns(self):
        self.client.force_login(self.payment_manager)
        html = self.client.get(reverse('sheets:payment')).content.decode()
        for header in ('Reward Base (R)', 'Manager 1 Performance (%)', 'Manager 2 Performance (%)', 'Addition 3 (Reward) (R)'):
            self.assertIn(header, html)
        self.assertNotRegex(html, r'data-field="rewardBase"\s+data-editable="true"')

        self.client.force_login(self.superuser)
        html = self.client.get(reverse('sheets:payment')).content.decode()
        self.assertRegex(html, r'data-field="rewardBase"\s+data-editable="true"')

    def test_hours_page_shows_payments_box_with_reward(self):
        self.client.force_login(self.employee)
        html = self.client.get(reverse('sheets:hours')).content.decode()
        self.assertIn('id="reward-payment"', html)
        self.assertIn('id="reward-info-btn"', html)
        self.assertNotIn('<div class="accordion-item d-none">', html)

    def test_verify_pages_have_performance_inputs(self):
        for actor, name in ((self.manager_1, 'sheets:verify_hours'), (self.supreme, 'sheets:supreme_verify_hours')):
            self.client.force_login(actor)
            response = self.client.get(reverse(name))
            self.assertEqual(response.status_code, 200, name)
            html = response.content.decode()
            self.assertIn('id="performance-m1"', html)
            self.assertIn('id="performance-m2"', html)
            # inputs sit inside the manager notes card, after the comments
            self.assertLess(html.index('id="manager-level-2-comment"'), html.index('id="performance-m1"'))
