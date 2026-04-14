from django.shortcuts import render, get_object_or_404
from ..models import Customer


def customer_detail(request, pk):
    customer = get_object_or_404(Customer, pk=pk)

    return render(request, "customer/detail.html", {
        "customer": customer
    })