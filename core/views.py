from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.db.models import F, Sum
from django.utils import timezone
from django.utils.timezone import now
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import models 
from datetime import date, timedelta

from inventario.models import *
from inventario.models import Movimiento as MovimientoBodega
from farmacia.models import *

def index(request):
    return render(request, "core/index.html")


@login_required
def dashboard(request):
    hoy = date.today()
    rol = request.user.perfil.rol

    # ---------------------------
    # MÉTRICAS GENERALES
    # ---------------------------

    total_usuarios = User.objects.count() if rol == "ADMIN" else None

    # Insumos críticos en bodega
    insumos_criticos = Insumo.objects.filter(
        stock__lte=F("stock_minimo")
    ).count()

    insumos_criticos_lista = Insumo.objects.filter(
        stock__lte=F("stock_minimo")
    )

    # Fármacos críticos en farmacia
    farmacos_criticos = Medicamento.objects.filter(
        stock__lte=F("stock_critico")
    ).count()

    farmacos_criticos_lista = Medicamento.objects.filter(
        stock__lte=F("stock_critico")
    )

    # Solicitudes
    solicitudes_pendientes_bodega = SolicitudReposicion.objects.filter(
        estado="PENDIENTE"
    ).count()

    solicitudes_pendientes_farmacia = SolicitudReposicion.objects.filter(
        estado="PENDIENTE", usuario=request.user
    ).count()

    # Movimientos recientes
    ult_mov_bodega = Movimiento.objects.order_by("-fecha")[:5]
    ult_mov_farmacia = MovimientoFarmacia.objects.order_by("-fecha")[:5]

    # ---------------------------------
    # ALERTAS DE VENCIMIENTO - BODEGA
    # ---------------------------------

    rango_30 = hoy + timedelta(days=30)
    rango_60 = hoy + timedelta(days=60)

    # Cantidades por rango
    vencen_30 = ItemFactura.objects.filter(
        vencimiento__isnull=False,
        vencimiento__gte=hoy,
        vencimiento__lte=rango_30
    ).count()

    vencen_30_60 = ItemFactura.objects.filter(
        vencimiento__isnull=False,
        vencimiento__gt=rango_30,
        vencimiento__lte=rango_60
    ).count()

    # Listas
    lotes_vencen_30 = ItemFactura.objects.filter(
        vencimiento__isnull=False,
        vencimiento__gte=hoy,
        vencimiento__lte=rango_30
    ).order_by("vencimiento")

    lotes_vencen_30_60 = ItemFactura.objects.filter(
        vencimiento__isnull=False,
        vencimiento__gt=rango_30,
        vencimiento__lte=rango_60
    ).order_by("vencimiento")


    # ---------------------------------
    # ALERTAS DE VENCIMIENTO - FARMACIA
    # ---------------------------------

    # Cantidades por rango
    vencimientos_farmacia_30 = LoteFarmacia.objects.filter(
        vencimiento__isnull=False,
        vencimiento__gte=hoy,
        vencimiento__lte=rango_30
    ).count()

    vencimientos_farmacia_30_60 = LoteFarmacia.objects.filter(
        vencimiento__isnull=False,
        vencimiento__gt=rango_30,
        vencimiento__lte=rango_60
    ).count()

    # Listas
    lotes_farmacia_vencen_30 = LoteFarmacia.objects.filter(
        vencimiento__isnull=False,
        vencimiento__gte=hoy,
        vencimiento__lte=rango_30
    ).order_by("vencimiento")

    lotes_farmacia_vencen_30_60 = LoteFarmacia.objects.filter(
        vencimiento__isnull=False,
        vencimiento__gt=rango_30,
        vencimiento__lte=rango_60
    ).order_by("vencimiento")

    # ---------------------------
    # DISPENSACIONES HOY
    # ---------------------------

    dispensaciones_hoy = MovimientoFarmacia.objects.filter(
        tipo="SALIDA",
        fecha__date=hoy
    ).aggregate(total=Sum("cantidad"))["total"] or 0

    # ---------------------------
    # CONTEXTO FINAL
    # ---------------------------

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

        # VENCIMIENTOS BODEGA
        "vencimientos_30": vencen_30,
        "vencimientos_30_60": vencen_30_60,
        "lotes_vencen_30": lotes_vencen_30,
        "lotes_vencen_30_60": lotes_vencen_30_60,

        # VENCIMIENTOS FARMACIA (CORRECTOS)
        "vencimientos_farmacia_30": vencimientos_farmacia_30,
        "vencimientos_farmacia_30_60": vencimientos_farmacia_30_60,
        "lotes_farmacia_vencen_30": lotes_farmacia_vencen_30,
        "lotes_farmacia_vencen_30_60": lotes_farmacia_vencen_30_60,

        "dispensaciones_hoy": dispensaciones_hoy,
    }

    return render(request, "core/dashboard.html", contexto)

def reports(request):
    # --- Filtros ---
    from_date = request.GET.get("from")
    to_date = request.GET.get("to")
    report_type = request.GET.get("type", "movimiento")  # por defecto bodega

    # ----------------------------
    # SELECCIÓN DE ORIGEN DE DATOS
    # ----------------------------
    
    movimientosB = Movimiento.objects.all().order_by("-fecha")
    
    movimientosF = MovimientoFarmacia.objects.all().order_by("-fecha")

    # ----------------------------
    # FILTROS DE FECHAS
    # ----------------------------
    if from_date:
        movimientos = movimientos.filter(fecha__date__gte=from_date)

    if to_date:
        movimientos = movimientos.filter(fecha__date__lte=to_date)

    context = {
        "movimientosB": movimientosB,
        "movimientosF": movimientosF,
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