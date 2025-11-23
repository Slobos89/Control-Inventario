from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages

def index(request):
    return render(request, "core/index.html")

def admin_dashboard(request):
    # Excluir al superusuario
    total_usuarios = User.objects.filter(is_superuser=False).count()

    return render(request, "core/admin_dashboard.html", {
        "total_usuarios": total_usuarios
    })

def jefe_bodega_dashboard(request):
    return render(request, "core/jefe_bodega_dashboard.html")

def jefe_farmacia_dashboard(request):
    return render(request, "core/jefe_farmacia_dashboard.html")

def reports(request):
    return render(request, "core/reports.html")

def login_view(request):
    if request.method == "POST":
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Buscar usuario por email
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            messages.error(request, "El correo no está registrado.")
            return render(request, "core/login.html")

        # Autenticar con username interno
        user = authenticate(request, username=user.username, password=password)

        if user:
            login(request, user)
            return redirect('index')
        else:
            messages.error(request, "Credenciales incorrectas.")

    return render(request, "core/login.html")

def logout_view(request):
    logout(request)
    return redirect('login')