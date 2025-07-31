from django.shortcuts import render, get_object_or_404
from .models import Phone


def catalog(request):
    phones = Phone.objects.all()

    # Получаем параметр сортировки
    sort = request.GET.get('sort')

    if sort == 'name':
        phones = phones.order_by('name')
    elif sort == 'min_price':
        phones = phones.order_by('price')
    elif sort == 'max_price':
        phones = phones.order_by('-price')

    return render(request, 'catalog.html', {'phones': phones})


def phone(request, slug):
    phone = get_object_or_404(Phone, slug=slug)
    return render(request, 'phone.html', {'phone': phone})