import json
import os
from functools import wraps

from apps.webhook.manager import WebhookDataManager
from apps.webhook.serializers import WebhookSerializer
from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt

API_NAME = os.getenv('API_NAME')
API_KEY = os.getenv('API_KEY')


def access_verification(view_func):
    """Декоратор проверки доступа. Проверяет доступен ключ доступа и его значение"""

    @wraps(view_func)
    def _wrapped_view(self, request, *args, **kwargs):
        try:
            data = json.loads(request.body.decode('unicode_escape'))
        except json.JSONDecodeError:
            return JsonResponse({'error': "Invalid JSON data", 'data': data})

        if API_NAME not in data:
            return JsonResponse({'error': "Access denied"})

        if data[API_NAME] != API_KEY:
            return JsonResponse({'error': "Access denied"})

        return view_func(self, request, data, *args, **kwargs)

    return _wrapped_view


@method_decorator(csrf_exempt, name="dispatch")
class WebhookView(View):
    """Вебхук, получающий данные от Tilda"""

    @access_verification
    def post(self, request, data, *args, **kwargs):
        serializer = WebhookSerializer()
        customer, order, products = serializer.serialize(data)
        manager = WebhookDataManager(customer, order, products)
        manager.save_data()
        return JsonResponse({})
