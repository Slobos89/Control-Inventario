from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import F, Sum
from django.utils import timezone
from django.utils.timezone import now
from datetime import date
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models 

from inventario.models import Insumo, Movimiento
from inventario.models import Movimiento as MovimientoBodega
from farmacia.models import Medicamento, MovimientoFarmacia, SolicitudReposicion

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
        stock__lte=F("stock_minimo")
    ).count()

    # insumos criticos en lista

    insumos_criticos_lista = Insumo.objects.filter(stock__lte=models.F("stock_minimo"))

    # Fármacos críticos en farmacia
    farmacos_criticos = Medicamento.objects.filter(
        stock__lte=F("stock_critico")
    ).count()

    # Fármacos críticos en lista
    farmacos_criticos_lista = Medicamento.objects.filter(stock__lte=models.F('stock_critico'))

    # Solicitudes pendientes para Jefe de Bodega
    solicitudes_pendientes_bodega = SolicitudReposicion.objects.filter(estado="PENDIENTE").count()

    # Solicitudes pendientes creadas por Farmacia (para mostrarles a ellos)
    solicitudes_pendientes_farmacia = SolicitudReposicion.objects.filter(estado="PENDIENTE",usuario=request.user).count()

    # Últimos movimientos (unificados)
    ult_mov_bodega = Movimiento.objects.order_by("-fecha")[:5]
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
        "insumos_criticos_lista": insumos_criticos_lista,
        "farmacos_criticos": farmacos_criticos,
        "farmacos_criticos_lista": farmacos_criticos_lista,
        "solicitudes_pendientes_bodega": solicitudes_pendientes_bodega,
        "solicitudes_pendientes_farmacia": solicitudes_pendientes_farmacia,
        "ult_mov_bodega": ult_mov_bodega,
        "ult_mov_farmacia": ult_mov_farmacia,
        "dispensaciones_hoy": dispensaciones_hoy,
    }

    return render(request, "core/dashboard.html", contexto)

def reports(request):
    # --- Filtros ---
    from_date = request.GET.get("from")
    to_date = request.GET.get("to")
    report_type = request.GET.get("type", "movimiento")

    movimientos = Movimiento.objects.all().order_by("-fecha")

    # Filtrar por fecha desde
    if from_date:
        movimientos = movimientos.filter(fecha__date__gte=from_date)

    # Filtrar por fecha hasta
    if to_date:
        movimientos = movimientos.filter(fecha__date__lte=to_date)

    context = {
        "movimientos": movimientos,
        "from": from_date,
        "to": to_date,
        "type": report_type,
    }

    return render(request, "core/reports.html", context)

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