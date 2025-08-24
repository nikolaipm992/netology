from celery import shared_task
from django.core.management import call_command
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

@shared_task
def do_import(file_path):
    """Асинхронный импорт товаров."""
    try:
        call_command('import_products', file_path)
        logger.info(f"Импорт из {file_path} завершен успешно")
    except Exception as e:
        logger.error(f"Ошибка при асинхронном импорте из {file_path}: {e}")
        raise

@shared_task
def send_email_task(subject, message, recipient_list):
    """Асинхронная отправка email."""
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            recipient_list,
            fail_silently=False,
        )
        logger.info(f"Email '{subject}' отправлен {recipient_list}")
    except Exception as e:
        logger.error(f"Ошибка при асинхронной отправке email '{subject}' to {recipient_list}: {e}")
        raise