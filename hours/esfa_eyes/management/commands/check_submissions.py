from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
import jdatetime as jdt 
from datetime import datetime, timedelta
import requests
import logging
from esfa_eyes.models import EsfaEyes  # Import your Report model

logger = logging.getLogger(__name__)
ESFAEYES_FIELD_NAMES = ['financial_info', 'international_finance_info', 'international_sales_info', 'products_info']
ESFAEYES_FIELD_TO_TELEGRAM_ID = {
    'financial_info': [78510872, 106243900],
    'international_finance_info': [63708619],
    'international_sales_info': [352162682],
    'products_info': [237628637],
}
BOSS_ID= 103813581
BOT_TOKEN= ""

DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

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
        
        overdue_count = 0
        sent_count = 0
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
                    print("outdated")
                elif diff_in_hours * 2 > interval_in_hours:
                    warning_subfields_dictionary[report_field].append(sub_field)
                    print("warning")
                else:
                    print("update")
                    
        self.send_telegram_alert(require_to_update_subfields_dictionary)
        
    
    def send_telegram_alert(self, subfields_dict):
        """Send Telegram alert to user"""
        return
        try:
            url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
            
            message = (
                f"⚠️ Hello {username}! Your report is overdue.\n"
                f"Please submit your report as soon as possible."
            )
            
            payload = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": "HTML"
            }
            
            response = requests.post(url, data=payload, timeout=10)
            response.raise_for_status()
            
            self.stdout.write(f"Telegram alert sent to {username}")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Failed to send Telegram message to {username}: {e}")
            self.stdout.write(
                self.style.ERROR(f"Failed to send Telegram alert to {username}: {e}")
            )
            return False