from django import forms
from django.contrib import admin, messages

from ckeditor_uploader.widgets import CKEditorUploadingWidget
from django.utils.translation import ngettext

from .models import MailSender
from .tasks import send_many_mails


class MailSenderForm(forms.ModelForm):
    content = forms.CharField(label="Содержимое письма", widget=CKEditorUploadingWidget())

    class Meta:
        model = MailSender
        fields = '__all__'


@admin.register(MailSender)
class MailSenderAdmin(admin.ModelAdmin):
    """Админка рассылки писем"""

    form = MailSenderForm
    list_display = ["subject", "is_active", "updated_at",]
    readonly_fields = ["updated_at",]
    actions = ['start_sender',]

    def start_sender(self, request, queryset):
        if not queryset.filter(is_active=True).exists():
            self.message_user(
                request,
                "Не все выбранные рассылки активны",
                level=messages.ERROR
            )
            return

        for sender in queryset:
            data = {
                "subject": sender.subject,
                "content": sender.content,
            }
            send_many_mails.delay(data)

        message = ngettext(
            'Рассылка запущена для %(count)d MailSender.',
            'Рассылка запущена для %(count)d MailSenders.',
            queryset.count(),
        ) % {'count': queryset.count()}
        self.message_user(request, message, level=messages.SUCCESS)

    start_sender.short_description = 'Запустить рассылку'