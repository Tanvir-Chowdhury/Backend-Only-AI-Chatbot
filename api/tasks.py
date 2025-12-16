from apscheduler.schedulers.background import BackgroundScheduler
from django.utils import timezone
from datetime import timedelta
from django.core.mail import send_mail
from django.conf import settings
from .models import ChatMessage

scheduler = BackgroundScheduler()

def cleanup_old_chats():
    """
    Background task to delete chat messages older than 30 days.
    This helps in maintaining database size and performance.
    """
    threshold = timezone.now() - timedelta(days=30)
    deleted_count, _ = ChatMessage.objects.filter(timestamp__lt=threshold).delete()
    print(f"Deleted {deleted_count} old chat messages.")

def send_welcome_email(user_email):
    """
    Background task to send a welcome email to new users.
    Uses Django's send_mail function with the configured SMTP backend.
    """
    subject = 'Welcome to Backend Only AI Chatbot'
    message = 'Thank you for registering with our AI Chatbot service.'
    email_from = settings.EMAIL_HOST_USER
    recipient_list = [user_email]
    
    try:
        send_mail(subject, message, email_from, recipient_list)
        print(f"Welcome email sent to {user_email}")
    except Exception as e:
        print(f"Failed to send email to {user_email}: {str(e)}")

def start_scheduler():
    """
    Initializes and starts the background scheduler.
    Adds the cleanup job to run daily.
    """
    if not scheduler.running:
        scheduler.add_job(cleanup_old_chats, 'interval', days=1, id='cleanup_old_chats', replace_existing=True)
        scheduler.start()
