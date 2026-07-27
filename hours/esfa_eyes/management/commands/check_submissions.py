import time
import random
from django.core.management.base import BaseCommand
import jdatetime as jdt 
import logging
from esfa_eyes.models import EsfaEyes

import requests
from requests.exceptions import ProxyError, Timeout, ConnectionError, RequestException

logger = logging.getLogger(__name__)
ESFAEYES_FIELD_NAMES = ['financial_info', 'international_finance_info', 'international_sales_info', 'products_info', 'kavosh_products_info', 'kia_products_info']
ESFAEYES_FIELD_TO_TELEGRAM_ID = {
    'financial_info': [78510872],                           # amiri
    'international_finance_info': [63708619],               # zahedi
    'international_sales_info': [352162682],                # dadashi
    'products_info': [237628637],                           # koolaji 
    'kavosh_products_info': [237628637],                    # koolaji 
    'kia_products_info': [375630609],                       # mohsen 
}
BOSS_ID = [103813581]                                       # morsali
ADMIN_ID = [293224143, 1320393742, 6372380391]
BOT_TOKEN= "8205869937:AAHcKkzCIZQYP6n55Mx6kG8yDrZT7NM-M7k"
BOT_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
PROXIES = {
    # 'http': 'http://127.0.0.1:2334',
    # 'https': 'http://127.0.0.1:2334',
}

TITLEMAPPING = {
	"balance_rials_official": 'موجودی حساب‌های رسمی (ریال)',
	"balance_rials": 'موجودی حساب‌های غیر رسمی (ریال)',
	"balance_dollars": 'موجودی دلاری',
	"montly_checks_received": 'چک‌های دریافتی (ریال)',
	"montly_checks_issued": 'چک‌های صادر شده (ریال)',
	"montly_installment": 'اقساط وام های دریافتی (ریال)',
	"montly_total_sales": 'فروش کل داخل (ریال)',
	"montly_international_total_sales": 'فروش کل خارج (دلار)',
	"individual_sales": 'فروش تفکیکی داخل (ریال)',
	"individual_sales_quantities": 'فروش تفکیکی داخل (تعداد)',
	"individual_sales_total_received": 'مجموع دریافتی تا این لحظه (ریال)',
	"individual_sales_check_received": 'مقدار چک دریافت شده (ریال)',
	"individual_sales_unknown": 'مقدار نامعلوم (ریال)',
	"international_individual_sales": 'فروش تفکیکی خارج (ریال)',
	"international_individual_sales_quantities": '(تعداد) فروش تفکیکی خارج',
	"ready_products": 'موجودی تولیدشده آماده تحویل',
	"ready_kavosh_products": 'موجودی کاوش تولیدشده آماده تحویل',
	"ready_kia_products": 'موجودی کیا تولیدشده آماده تحویل',
	"unproducable_shortage_product": 'موجودی غ.ق تولید به دلیل کسری',
	"unproducable_shortage_kia_product": 'موجودی کیا غ.ق تولید به دلیل کسری',
	"unproducable_shortage_kavosh_product": 'موجودی کاوش غ.ق تولید به دلیل کسری',
	"unproduced_workshop_inventory": 'موجودی کارگاه تولید نشده',
	"unproduced_kavosh_workshop_inventory": 'موجودی کاوش کارگاه تولید نشده',
	"unproduced_kia_workshop_inventory": 'موجودی کیا کارگاه تولید نشده',
	"deliverd_1404": 'تحویل داده شده از ابتدای سال',
	"deliverd_1403": 'کل تحویلی در سال 1403',
	"deliverd_1402": 'کل تحویلی در سال 1402',
	"deliverd_1401": 'کل تحویلی در سال 1401',
	"deliverd_1400": 'کل تحویلی در سال 1400',
	"deliverd_1399": 'کل تحویلی در سال 99',
    "turkiye_inventory": 'موجودی ترکیه',
	"china_production_orders": 'سفارشات چین درحال تولید',
	"total_insured_staffs": 'تعداد کارکنان بیمه‌ای',
	"total_insured_non_staffs": 'تعداد بیمه‌ای بدون حضور',
	"total_uninsured_staffs": 'تعداد کارکنان غیر بیمه',
	"total_salary_paid": 'مجموع کل حقوق (ریال)',
	"total_insurance_paid": 'مجموع بیمه پرداختی (ریال)'
}

#=====================================================================================
class Command(BaseCommand):
    help = 'Checks for overdue reports and sends Telegram alerts'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Check for overdue reports without sending actual messages',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        self.stdout.write(f"Checking for overdue reports... Dry run: {dry_run}")
        if dry_run:
            self.dry_run()
            self.alert(True)
            return

        self.alert()
    
    #########################################################################
    ################################ DRY RUN ################################
    def dry_run(self):
        if not self._is_inside_valid_hours():
            print("bot is sleeping...")
            return
        persian_subfields =["محموع حقوق پرداختی", "وام های گرفته شده", "موجودی حساب‌های غیر رسمی"]
        formatted_persian_require_to_update_subfields = '\n'.join(f"    \\- {s}" for s in persian_subfields)
        
        warning_subfields =["فروش کل داخل", "موجودی دلاری"]
        formatted_persian_warning_subfields = '\n'.join(f"    \\- {s}" for s in warning_subfields)
        
        message = f""" *درود*
مدتی است که گزارش *Esfa Eyes* خود را ارسال نکرده اید\\.
لطفا در اسرع وقت گزارشات زیر را اپدیت نمایید\\:
‏🔴
{formatted_persian_require_to_update_subfields}
‏🟠
{formatted_persian_warning_subfields}
[Update in *ESFA Eyes*](https://kavosh\\.online/hours/esfa_eyes_dashbord)"""

        self.send_telegram_message_with_retry(ADMIN_ID[0], message)
    

    #########################################################################
    ################################ Private Method ################################
    def _is_inside_valid_hours(self):
        current_time = jdt.datetime.now()
        if current_time.weekday() == 4:  # Friday is weekday 4
            return False
        if current_time.hour < 6:
            return False
        return True

    def _escape_markdown_v2(self, text):
        escape_chars = r'_*[]()~`>#+-=|{}.!'
        return ''.join(f'\\{char}' if char in escape_chars else char for char in text)

    def _send_telegram_api_message(self, chat_id, message, timeout=30):
        """Send a single Telegram API message"""
        payload = {
            "chat_id": chat_id,
            "text": message,
            "parse_mode": "MarkdownV2"
        }
        try:
            response = requests.post(
                BOT_URL + "sendMessage",
                data=payload,
                timeout=timeout,
                proxies=PROXIES
            )
            response.raise_for_status()
            return response
        except (ProxyError, Timeout, ConnectionError) as e:
            logger.error(f"Network-related error sending to {chat_id}: {e}")
            raise
        except RequestException as e:
            logger.error(f"Failed to send Telegram message to {chat_id}: {e}")
            raise
        
    def _get_user_name(self, user_id):
        user_name_map = {
            78510872: "Amiri",
            63708619: "Zahedi", 
            352162682: "Dadashi",
            237628637: "Colaji",
            147770648: "Hajihasani",
            375630609: "kazempourian"
        }
        return user_name_map.get(user_id, f"User_{user_id}")
    
    #########################################################################
    ################################ Public Method ################################
    def alert(self, dry_run = False):
        if not dry_run and not self._is_inside_valid_hours():
            print("bot is sleeping...")
            return
        Eyes_report = EsfaEyes.objects.latest('year')
        if not Eyes_report:
            self.stdout.write("No valid report data found.")
            return
        
        current_date = jdt.datetime.now()
        
        subfields_dictionary = {field_name: {"require_to_update": [], "warning": []} for field_name in ESFAEYES_FIELD_NAMES}
        
        total_require_update = 0
        total_warning = 0
        user_status = {}
        
        for report_field in ESFAEYES_FIELD_NAMES:
            for sub_field in Eyes_report[report_field]:
                interval_in_hours =  Eyes_report[report_field][sub_field]['UPDATE_INTERVAL_DAYS']*24
                last_modify_time =  Eyes_report[report_field][sub_field]['last_modify_time']
                parsed_last_modify_time = jdt.datetime.strptime(last_modify_time, DATE_FORMAT)
                diff = current_date - parsed_last_modify_time
                diff_in_hours = diff.total_seconds() / 3600

                if diff_in_hours > interval_in_hours:
                    subfields_dictionary[report_field]["require_to_update"].append(sub_field)
                    total_require_update += 1
                elif diff_in_hours * 2 > interval_in_hours:
                    subfields_dictionary[report_field]["warning"].append(sub_field)
                    total_warning += 1
        
        for field_name, user_ids in ESFAEYES_FIELD_TO_TELEGRAM_ID.items():
            for user_id in user_ids:
                user_status[user_id] = {
                    'field': field_name,
                    'require_update_count': len(subfields_dictionary[field_name]["require_to_update"]),
                    'warning_count': len(subfields_dictionary[field_name]["warning"]),
                    'total_responsible': len(Eyes_report[field_name])
                }
        if not dry_run:
            self.send_warning_alerts_users(subfields_dictionary)
        self.send_warning_alerts_admin(Eyes_report, subfields_dictionary, total_require_update, total_warning, user_status, dry_run)
    
    def send_warning_alerts_users(self, subfields_dict):
        for field_name in subfields_dict:   # financial_info, international_finance_info, ...
            if subfields_dict[field_name]["require_to_update"]:
                persian_require_to_update_subfields = [TITLEMAPPING[sub] for sub in subfields_dict[field_name]['require_to_update']]
                formatted_persian_require_to_update_subfields = '\n'.join(f"    \\-{self._escape_markdown_v2(s)}" for s in persian_require_to_update_subfields)
                persian_warning_subfields = [TITLEMAPPING[sub] for sub in subfields_dict[field_name]['warning']]
                formatted_persian_warning_subfields = '\n'.join(f"    \\-{self._escape_markdown_v2(s)}" for s in persian_warning_subfields)
                
                message = f""" *درود*
مدتی است که گزارش *Esfa Eyes* خود را ارسال نکرده اید\\.
لطفا در اسرع وقت گزارشات زیر را اپدیت نمایید\\:
‏🔴
{formatted_persian_require_to_update_subfields} 
‏🟠
{formatted_persian_warning_subfields} 
[Update in *ESFA Eyes*](https://kavosh\\.online/hours/esfa_eyes_dashbord)
"""
                for chat_id in ESFAEYES_FIELD_TO_TELEGRAM_ID[field_name]:
                    success = self.send_telegram_message_with_retry(chat_id, message)
                    if not success:
                        logger.error(f"Failed to send message to {chat_id} after all retry attempts")
                        self.stdout.write(
                            self.style.ERROR(f"Failed to send message to {chat_id} after all retry attempts")
                        )

    def send_warning_alerts_admin(self, Eyes_report, subfields_dict, total_require_update, total_warning, user_status, dry_run = False):
        # Create comprehensive admin overview message
        overview_message = f"""*ESFA Eyes Status Report*

    *📈 Overall Statistics:*
    • 🔴 : {total_require_update}
    • 🟠 : {total_warning}
    • ✅ : {sum(len(Eyes_report[field]) for field in ESFAEYES_FIELD_NAMES) - total_require_update - total_warning}

\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=
    *👥 User Status Breakdown:*
    """
        
        # Add user-specific status
        for user_id, status in user_status.items():
            user_name = self._get_user_name(user_id)  # You'll need to implement this method
            overview_message += f"""
    • *{user_name}* \\({status['field']}\\):
    \\- 🔴 : {status['require_update_count']}
    \\- 🟠 : {status['warning_count']}
    \\- 📋 Total responsible: {status['total_responsible']}
    \\- 📊 Completion rate: {round((status['total_responsible'] - status['require_update_count'] - status['warning_count']) / status['total_responsible'] * 100)}%
    """
        
        # Add field-by-field breakdown
        overview_message += "\n\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\=\\="
        overview_message += "\n*📋 Field\\-by\\-Field Breakdown:*"
        for field_name in ESFAEYES_FIELD_NAMES:
            total_subfields = len(Eyes_report[field_name])
            req_update = len(subfields_dict[field_name]["require_to_update"])
            warnings = len(subfields_dict[field_name]["warning"])
            
            overview_message += f"""
    • *{field_name.replace('_', ' ').title()}:*
    \\- 🔴 {req_update} \\| 🟠 {warnings} \\| ✅ {total_subfields - req_update - warnings}
    \\- Status: {'🔴 Critical' if req_update > 0 else '🟠 Warning' if warnings > 0 else '✅ Good'}
    """
        
        overview_message += f"""

    *⏰ Last Check:* {jdt.datetime.now().strftime('%Y_%m_%d %H:%M:%S')}
    """
        for admin_id in ADMIN_ID:
            success = self.send_telegram_message_with_retry(admin_id, overview_message)
            if not success:
                logger.error(f"ADMIN---Failed to send overview to admin {admin_id} after all retry attempts")
                self.stdout.write(
                    self.style.ERROR(f"ADMIN---Failed to send overview to admin {admin_id} after all retry attempts")
                )
        if not dry_run:
            for boss_id in BOSS_ID:
                success = self.send_telegram_message_with_retry(boss_id, overview_message)
                if not success:
                    logger.error(f"BOSS---Failed to send overview to boss {boss_id}")
            
    def send_telegram_message_with_retry(self, chat_id, message, max_retries=10):
        for attempt in range(max_retries + 1):
            try:
                response = self._send_telegram_api_message(chat_id, message)
                if response and response.status_code == 200:
                    self.stdout.write(
                        self.style.SUCCESS(f"Message sent successfully to {chat_id} on attempt {attempt + 1}")
                    )
                    return True
                else:
                    raise RequestException(f"HTTP {response.status_code if response else 'No response'}")
                    
            except (ProxyError, Timeout, ConnectionError) as e:
                if attempt < max_retries:
                    base_delay = 60  # 1 minute base delay
                    exponential_delay = min(60 * (2 ** attempt), 300)  # Max 5 minutes
                    jitter = random.uniform(0, 30)  # 0-30 seconds random jitter
                    total_delay = base_delay + exponential_delay + jitter
                    
                    logger.warning(
                        f"Network error sending to {chat_id} (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                        f"Retrying in {total_delay:.1f} seconds..."
                    )
                    self.stdout.write(
                        self.style.WARNING(
                            f"Network error for {chat_id} (attempt {attempt + 1}). "
                            f"Retrying in {total_delay:.1f} seconds..."
                        )
                    )
                    time.sleep(total_delay)
                else:
                    logger.error(f"Network error sending to {chat_id} after {max_retries + 1} attempts: {e}")
                    return False
                    
            except RequestException as e:
                if hasattr(e, 'response') and e.response is not None and e.response.status_code == 400:
                    try:
                        error_text = e.response.text if hasattr(e.response, 'text') else str(e.response.content)
                        # Try to parse JSON error response
                        import json
                        try:
                            error_data = json.loads(e.response.text)
                            error_description = error_data.get('description', 'Unknown error')
                            error_code = error_data.get('error_code', 400)
                        except (json.JSONDecodeError, AttributeError):
                            error_description = error_text
                            error_code = 400
                    except Exception:
                        error_description = str(e)
                        error_code = 400
                    
                    logger.error(
                        f"Telegram API 400 error for {chat_id} - Code: {error_code}, "
                        f"Description: {error_description}"
                    )
                    self.stdout.write(
                        self.style.ERROR(
                            f"Telegram API error for {chat_id}: {error_description}"
                        )
                    )
                    
                    # Check if it's specifically a "user hasn't started bot" error
                    if "chat not found" in error_description.lower() or "bot was blocked" in error_description.lower():
                        logger.info(f"User {chat_id} hasn't started the bot or blocked it. Skipping retries.")
                        return False
                    else:
                        # For other 400 errors (like parsing errors), don't retry but show the actual error
                        return False

                if attempt < max_retries:
                    # For other request exceptions, use shorter delays
                    base_delay = 30  # 30 seconds base delay
                    exponential_delay = min(30 * (2 ** attempt), 120)  # Max 2 minutes
                    jitter = random.uniform(0, 15)  # 0-15 seconds random jitter
                    total_delay = base_delay + exponential_delay + jitter
                    
                    logger.warning(
                        f"Request error sending to {chat_id} (attempt {attempt + 1}/{max_retries + 1}): {e}. "
                        f"Retrying in {total_delay:.1f} seconds..."
                    )
                    self.stdout.write(
                        self.style.WARNING(
                            f"Request error for {chat_id} (attempt {attempt + 1}). "
                            f"Retrying in {total_delay:.1f} seconds..."
                        )
                    )
                    time.sleep(total_delay)
                else:
                    logger.error(f"Request error sending to {chat_id} after {max_retries + 1} attempts: {e}")
                    return False
                    
            except Exception as e:
                # For unexpected exceptions, don't retry
                logger.error(f"Unexpected error sending to {chat_id}: {e}")
                self.stdout.write(
                    self.style.ERROR(f"Unexpected error for {chat_id}: {e}")
                )
                return False
                
        return False
