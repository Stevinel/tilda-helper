from django.apps import AppConfig


class MailSendersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.mail_senders'
    verbose_name = "Рассылка писем"
