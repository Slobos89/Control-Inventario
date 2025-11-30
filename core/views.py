from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import F, Sum
from django.utils.timezone import now
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from inventario.models import Insumo
from inventario.models import Movimiento as MovimientoBodega
from farmacia.models import Medicamento, MovimientoFarmacia

def index(request):
    return render(request, "core/index.html")

@login_required
def dashboard(request):

    rol = request.user.perfil.rol

    # ---------------------------
    # MÉTRICAS GENERALES
    # ---------------------------

    total_usuarios = User.objects.count() if rol == "ADMIN" else None

    # Insumos críticos en bodega
    insumos_criticos = Insumo.objects.filter(
        stock__lt=F("stock_minimo")
    ).count()

    # Fármacos críticos en farmacia
    farmacos_criticos = Medicamento.objects.filter(
        stock__lt=5
    ).count()

    # Últimos movimientos (unificados)
    ult_mov_bodega = MovimientoBodega.objects.order_by("-fecha")[:5]
    ult_mov_farmacia = MovimientoFarmacia.objects.order_by("-fecha")[:5]

    # Dispensaciones HOY (solo farmacia)
    dispensaciones_hoy = MovimientoFarmacia.objects.filter(
        tipo="SALIDA",
        fecha__date=date.today()
    ).aggregate(total=Sum("cantidad"))["total"] or 0

    contexto = {
        "rol": rol,
        "total_usuarios": total_usuarios,
        "insumos_criticos": insumos_criticos,
        "farmacos_criticos": farmacos_criticos,
        "ult_mov_bodega": ult_mov_bodega,
        "ult_mov_farmacia": ult_mov_farmacia,
        "dispensaciones_hoy": dispensaciones_hoy,
    }

    return render(request, "core/dashboard.html", contexto)

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