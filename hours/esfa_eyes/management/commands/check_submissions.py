import time
import random
from django.core.management.base import BaseCommand
import jdatetime as jdt 
import logging
from esfa_eyes.models import EsfaEyes

import requests
from requests.exceptions import ProxyError, Timeout, ConnectionError, RequestException

logger = logging.getLogger(__name__)
ESFAEYES_FIELD_NAMES = ['financial_info', 'international_finance_info', 'international_sales_info', 'products_info']
ESFAEYES_FIELD_TO_TELEGRAM_ID = {
    'financial_info': [78510872],               # amiri
    'international_finance_info': [63708619],   # zahedi
    'international_sales_info': [352162682],    # dadashi
    'products_info': [237628637],               # colaji
}
BOSS_ID = [103813581]
ADMIN_ID = [293224143, 1320393742, 6372380391]
BOT_TOKEN= "7985758239:AAECktRZy7htev_itYxdriN5YPJXyLgs4EI"
BOT_URL = f"https://api.telegram.org/bot{BOT_TOKEN}/"
DATE_FORMAT = '%Y-%m-%d %H:%M:%S'
PROXIES = {
    'http': 'http://127.0.0.1:12334',
    'https': 'http://127.0.0.1:12334',
}

TITLEMAPPING = {
	"balance_rials_official": 'موجودی حساب‌های رسمی',
	"balance_rials": 'موجودی حساب‌های غیر رسمی',
	"balance_dollars": 'موجودی دلاری',
	"montly_checks_recieved": 'چک‌های دریافتی',
	"montly_checks_issued": 'چک‌های صادر شده',
	"montly_installment": 'اقساط وام های دریافتی',
	"montly_total_sales": 'فروش کل داخل',
	"montly_international_total_sales": 'فروش کل خارج',
	"individual_sales": 'فروش تفکیکی داخل',
	"international_individual_sales": 'فروش تفکیکی خارج',
	"ready_products": 'موجودی تولیدشده آماده تحویل',
	"unproduced_workshop_inventory": 'موجودی کارگاه تولید نشده',
	"turkiye_inventory": 'موجودی ترکیه',
	"china_production_orders": 'سفارشات چین درحال تولید',
	"total_insured_staffs": 'تعداد کارکنان بیمه‌ای',
	"total_uninsured_staffs": 'تعداد کارکنان غیر بیمه',
	"total_salary_paid": 'مجموع کل حقوق',
	"total_insurance_paid": 'مجموع بیمه پرداختی'
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
            return

        self.alert()
    
    def dry_run(self):
        if not self.is_inside_valid_hours():
            print("bot is sleeping...")
            return
        persian_subfields =["محموع حقوق پرداختی", "وام های گرفته شده"]
        formatted_subfields = '\n'.join(f"    \\- {s}" for s in persian_subfields)
        
        message=f""" *درود*
مدتی است که گزارش *ESFA Eyes* خود را ارسال نکرده اید\\.
لطفا در اسرع وقت گزارشات زیر را اپدیت نمایید\\:
{formatted_subfields} 
[ESFA Eyes](https://kavosh\\.online/hours/esfa_eyes_dashbord)
"""
        self.send_telegram_message_with_retry(ADMIN_ID[0], message)
    
    def is_inside_valid_hours(self):
        current_time = jdt.datetime.now().hour
        if current_time < 6:
            return False
        return True
        
    def alert(self):
        if not self.is_inside_valid_hours():
            print("bot is sleeping...")
            return
        Eyes_report = EsfaEyes.objects.latest('year')
        if not Eyes_report:
            self.stdout.write("No valid report data found.")
            return
        
        current_date = jdt.datetime.now()
        
        require_to_update_subfields_dictionary = {field_name: [] for field_name in ESFAEYES_FIELD_NAMES}
        warning_subfields_dictionary = {field_name: [] for field_name in ESFAEYES_FIELD_NAMES}
        
        for report_field in ESFAEYES_FIELD_NAMES:
            for sub_field in Eyes_report[report_field]:
                interval_in_hours =  Eyes_report[report_field][sub_field]['UPDATE_INTERVAL_DAYS']*24
                last_modify_time =  Eyes_report[report_field][sub_field]['last_modify_time']
                parsed_last_modify_time = jdt.datetime.strptime(last_modify_time, DATE_FORMAT)
                diff = current_date - parsed_last_modify_time
                diff_in_hours = diff.total_seconds() / 3600

                if diff_in_hours > interval_in_hours:
                    require_to_update_subfields_dictionary[report_field].append(sub_field)
                elif diff_in_hours * 2 > interval_in_hours:
                    warning_subfields_dictionary[report_field].append(sub_field)
                    
        self.send_warning_alerts_users(require_to_update_subfields_dictionary)
    
    def send_warning_alerts_users(self, subfields_dict):
        """Send Telegram alert to user with retry logic"""
        for field_name in subfields_dict:   # international_finance_info, ...
            if subfields_dict[field_name]:  # ['balance_dollars', 'china_production_orders'], ...
                print("\n-----")
                print(field_name)
                print(subfields_dict[field_name])
                persian_subfields = [TITLEMAPPING[sub] for sub in subfields_dict[field_name]]
                formatted_subfields = '\n'.join(f"    \\-{s}" for s in persian_subfields)
                print(formatted_subfields)
                
                message = f""" *درود*
مدتی است که گزارش *Esfa Eyes* خود را ارسال نکرده اید\\.
لطفا در اسرع وقت گزارشات زیر را اپدیت نمایید\\:
{formatted_subfields} 
[ESFA Eyes](https://kavosh\\.online/hours/esfa_eyes_dashbord)
"""
                for chat_id in ESFAEYES_FIELD_TO_TELEGRAM_ID[field_name]:
                    success = self.send_telegram_message_with_retry(chat_id, message)
                    if not success:
                        logger.error(f"Failed to send message to {chat_id} after all retry attempts")
                        self.stdout.write(
                            self.style.ERROR(f"Failed to send message to {chat_id} after all retry attempts")
                        )

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
                    logger.info(f"User {chat_id} hasn't started the bot yet (HTTP 400). Skipping retries.")
                    self.stdout.write(
                        self.style.WARNING(f"User {chat_id} hasn't started the bot yet. Message not delivered.")
                    )
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