from typing import Type
import logging
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.db.models.signals import post_save
from django.dispatch import receiver, Signal
from django_rest_passwordreset.signals import reset_password_token_created

from backend.models import ConfirmEmailToken, User, Order

logger = logging.getLogger(__name__)

new_user_registered = Signal()
new_order = Signal()

@receiver(reset_password_token_created)
def password_reset_token_created(sender, instance, reset_password_token, **kwargs):
    """
    Отправляем письмо с токеном для сброса пароля
    """
    try:
        msg = EmailMultiAlternatives(
            f"Password Reset Token for {reset_password_token.user}",
            reset_password_token.key,
            settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
            [reset_password_token.user.email]
        )
        msg.send()
        logger.info(f"Отправлен токен сброса пароля для пользователя {reset_password_token.user.email}")
    except Exception as e:
        logger.error(f"Ошибка отправки email для сброса пароля пользователю {reset_password_token.user.email}: {e}")

@receiver(post_save, sender=User)
def new_user_registered_signal(sender: Type[User], instance: User, created: bool, **kwargs):
    """
    отправляем письмо с подтверждением почты
    """
    if created and not instance.is_active:
        try:
            token, _ = ConfirmEmailToken.objects.get_or_create(user_id=instance.pk)
            
            msg = EmailMultiAlternatives(
                f"Подтверждение регистрации для {instance.email}",
                f"Ваш токен подтверждения: {token.key}",
                settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
                [instance.email]
            )
            msg.send()
            logger.info(f"Отправлено письмо подтверждения для пользователя {instance.email}")
        except Exception as e:
            logger.error(f"Ошибка отправки email подтверждения для пользователя {instance.email}: {e}")

@receiver(new_order)
def new_order_signal(user_id, **kwargs):
    """
    отправляем письмо при создании нового заказа
    """
    try:
        user = User.objects.get(id=user_id)

        customer_msg = EmailMultiAlternatives(
            "Подтверждение заказа",
            "Ваш заказ успешно оформлен и передан на обработку",
            settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
            [user.email]
        )
        customer_msg.send()

        admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@shop.ru')
        admin_msg = EmailMultiAlternatives(
            "Новый заказ",
            f"Пользователь {user.email} оформил новый заказ",
            settings.DEFAULT_FROM_EMAIL or settings.EMAIL_HOST_USER,
            [admin_email]
        )
        admin_msg.send()
        
        logger.info(f"Отправлены уведомления о заказе пользователю {user.email} и администратору {admin_email}")
    except User.DoesNotExist:
        logger.error(f"Пользователь с ID {user_id} не найден")
    except Exception as e:
        logger.error(f"Ошибка отправки email о заказе для пользователя ID {user_id}: {e}")