from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from datetime import timedelta
from .models import ChatMessage

def cleanup_old_chats():
    threshold = timezone.now() - timedelta(days=30)
    deleted_count, _ = ChatMessage.objects.filter(timestamp__lt=threshold).delete()
    print(f"Deleted {deleted_count} old chat messages.")

def send_welcome_email(user_email):
    print(f"Sending welcome email to {user_email}...")

def start_scheduler():
    scheduler = BackgroundScheduler()
    scheduler.add_job(cleanup_old_chats, 'interval', days=1, id='cleanup_old_chats', replace_existing=True)
    scheduler.start()
