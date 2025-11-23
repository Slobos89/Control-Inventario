from django.shortcuts import render

def inventory_list(request):
    return render(request, "inventario/inventory_list.html")

def register_entry(request):
    return render(request, "inventario/register_entry.html")

def review_received(request):
    return render(request, "inventario/review_received.html")

def requests_view(request):
    return render(request, "inventario/requests.html")