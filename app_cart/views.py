import datetime
import time

from django.contrib import messages
from django.http import HttpResponseRedirect
from django.views.decorators.http import require_POST


@require_POST
def cart_add(request):
    """Функция заглушка для получения данных в корзину"""
    messages.success(request, 'Товар добавлен в корзину!')
    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
