from django.shortcuts import render

def dispense(request):
    return render(request, "farmacia/dispense.html")
