from django.core.management.base import BaseCommand
from django.utils import timezone
from django.contrib.auth.models import User
import jdatetime as jdt 
from datetime import datetime, timedelta
import requests
import logging
from esfa_eyes.models import EsfaEyes  # Import your Report model

logger = logging.getLogger(__name__)

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
        
        report = EsfaEyes.objects.last()
        print(datetime.now())
        print(jdt.datetime.now())
        
        return
        # Calculate next due time
        next_due = report.last_submission + timedelta(hours=report.update_interval_hours)
        
        if timezone.now() > next_due:
            overdue_count += 1
            self.stdout.write(
                f"User {report.user.username} has overdue report. "
                f"Last submission: {report.last_submission}. "
                f"Next due: {next_due}"
            )
            
            # Only send if user has Telegram chat ID
            if report.telegram_chat_id:
                if not dry_run:
                    success = self.send_telegram_alert(report.telegram_chat_id, report.user.username)
                    if success:
                        sent_count += 1
                else:
                    self.stdout.write(f"Would send Telegram alert to {report.user.username}")
            else:
                self.stdout.write(f"User {report.user.username} has no Telegram chat ID")
        
        # Summary
        self.stdout.write(
            self.style.SUCCESS(
                f"Check completed. {overdue_count} overdue reports found. "
                f"{sent_count} alerts sent."
            )
        )
    
    def send_telegram_alert(self, chat_id, username):
        """Send Telegram alert to user"""
        try:
            token = "YOUR_TELEGRAM_BOT_TOKEN"  # Use environment variable in production!
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            
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