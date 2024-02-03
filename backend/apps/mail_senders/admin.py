from config import settings
from sentry_sdk import capture_message
from ckeditor_uploader.widgets import CKEditorUploadingWidget

from .tasks import send_many_mails
from ..utils import MessageSender
from .models import MailSender
from ..customers.models import Customer

from django import forms
from django.contrib import admin, messages
from django.utils.translation import ngettext


class MailSenderForm(forms.ModelForm):
    content = forms.CharField(label='Содержимое письма', widget=CKEditorUploadingWidget())

    class Meta:
        model = MailSender
        fields = '__all__'


@admin.register(MailSender)
class MailSenderAdmin(admin.ModelAdmin):
    """Админка рассылки писем"""

    form = MailSenderForm
    list_display = [
        'subject',
        'is_active',
        'updated_at',
    ]
    readonly_fields = [
        'updated_at',
    ]
    actions = [
        'start_sender',
    ]

    def start_sender(self, request, queryset):
        if not queryset.filter(is_active=True).exists():
            self.message_user(request, 'Не все выбранные рассылки активны', level=messages.ERROR)
            return

        if settings.DEBUG:
            clients = Customer.objects.filter(email='test@test.ru')
        else:
            clients = Customer.objects.filter(is_receive_mails=True)

        for sender in queryset:
            MessageSender().send_success_message(f"Начинаю рассылку - '{sender.subject}'")

            for client in clients:
                try:
                    data = {
                        'subject': sender.subject,
                        'content': sender.content,
                        'client_email': client.email,
                    }
                    send_many_mails.delay(data)
                except Exception as e:
                    capture_message(f'Mail sender error: {e}')
                    continue

        MessageSender().send_success_message(f'Будет отправлено: {clients.count()} писем')

        message = ngettext(
            'Рассылка запущена для %(count)d MailSender.',
            'Рассылка запущена для %(count)d MailSenders.',
            queryset.count(),
        ) % {'count': queryset.count()}
        self.message_user(request, message, level=messages.SUCCESS)

    start_sender.short_description = 'Запустить рассылку'
