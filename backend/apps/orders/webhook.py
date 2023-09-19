from django.http import JsonResponse
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_exempt


@method_decorator(csrf_exempt, name="dispatch")
class WebhookView(View):
    def post(self, request, *args, **kwargs):
        print(request.__dict__, 'dict')
        print(request.headers, 'headers')
        print(request.POST.__dict__, 'post dict')
        print(request.body, request.META, 'body and meta')
        return JsonResponse({})
