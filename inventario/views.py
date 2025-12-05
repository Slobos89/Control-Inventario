from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.forms import inlineformset_factory 
from farmacia.models import SolicitudReposicion, ItemSolicitud
from .models import *
from .forms import (
    FacturaIngresoForm,
    UploadFileForm,
)
from django.db import transaction
import csv
import io

# ----------------------
# LISTA DE INVENTARIO
# ----------------------
@login_required
def inventory_list(request):
    insumos = Insumo.objects.all().order_by("nombre")
    return render(request, "inventario/inventory_list.html", {"insumos": insumos})


# ----------------------
# INGRESO POR FACTURA
# ----------------------
@login_required
def register_entry(request):
    insumos = Insumo.objects.all().order_by("nombre")

    if request.method == "POST":
        factura_form = FacturaIngresoForm(request.POST)

        if factura_form.is_valid():
            factura = factura_form.save(commit=False)
            factura.usuario = request.user
            factura.save()

            # Capturar items dinámicamente
            index = 1
            while True:
                insumo_key = f"insumo_{index}"
                cantidad_key = f"cantidad_{index}"
                lote_key = f"lote_{index}"
                venc_key = f"vencimiento_{index}"

                if insumo_key not in request.POST:
                    break  # No hay más filas

                insumo_id = request.POST.get(insumo_key)

                if not insumo_id:
                    index += 1
                    continue

                cantidad = int(request.POST.get(cantidad_key, 0))

                insumo = get_object_or_404(Insumo, pk=insumo_id)

                ItemFactura.objects.create(
                    factura=factura,
                    insumo=insumo,
                    cantidad=cantidad,
                    lote=request.POST.get(lote_key),
                    vencimiento=request.POST.get(venc_key) or None
                )

                Movimiento.objects.create(
                    insumo=insumo,
                    tipo="INGRESO",
                    cantidad=cantidad,
                    usuario=request.user,
                    factura=factura
                )

                insumo.stock += cantidad
                insumo.save()

                index += 1

            messages.success(request, "Factura registrada correctamente.")
            return redirect("inventario:facturas_list")

        else:
            messages.error(request, "Corrige los errores del formulario.")

    else:
        factura_form = FacturaIngresoForm()

    return render(request, "inventario/register_entry.html", {
        "form": factura_form,
        "insumos": insumos,
    })


@login_required
def facturas_list(request):
    facturas = FacturaIngreso.objects.all().order_by("-fecha_emision")

    return render(request, "inventario/facturas_list.html", {
        "facturas": facturas
    })

@login_required
def factura_detalle(request, pk):
    factura = get_object_or_404(FacturaIngreso, pk=pk)
    items = factura.items.all()

    return render(request, "inventario/factura_detalle.html", {
        "factura": factura,
        "items": items
    })


@login_required
def solicitudes_listar(request):
    solicitudes = SolicitudReposicion.objects.order_by("-fecha")
    return render(request, "inventario/solicitudes_listar.html", {
        "solicitudes": solicitudes
    })


def import_inventory(request):
    if request.method == "POST":
        file = request.FILES.get("file")

        if not file.name.endswith(".csv"):
            messages.error(request, "El archivo debe ser un CSV.")
            return redirect("import_inventory")

        decoded = file.read().decode("utf-8-sig")  # <- ELIMINA BOM AUTOMÁTICAMENTE

        f = io.StringIO(decoded)
        reader = csv.DictReader(f, delimiter=';')

        
        # NORMALIZAR encabezados
        reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]

        # Verificar que existan
        required = {"nombre", "unidad", "stock", "stock_minimo"}

        if not required.issubset(set(reader.fieldnames)):
            messages.error(request, f"El archivo CSV debe contener estas columnas: {', '.join(required)}")
            return redirect("import_inventory")

        for row in reader:
            nombre = row["nombre"].strip()
            unidad = row["unidad"].strip()
            stock = int(row["stock"])
            stock_minimo = int(row["stock_minimo"])

            insumo, created = Insumo.objects.get_or_create(
                nombre=nombre,
                defaults={"unidad": unidad, "stock": stock, "stock_minimo": stock_minimo}
            )

            if not created:
                # Si existe → actualiza stock
                insumo.unidad = unidad
                insumo.stock = stock
                insumo.stock_minimo = stock_minimo
                insumo.save()

        messages.success(request, "Inventario importado correctamente.")
        return redirect("inventory_list")

    return render(request, "inventario/import_inventory.html")

@login_required
def solicitud_detalle(request, pk):
    solicitud = get_object_or_404(SolicitudReposicion, pk=pk)
    items = solicitud.items.all()

    if request.method == "POST":
        accion = request.POST.get("accion")

        if accion == "aprobar":
            for item in solicitud.items.all():
                insumo = item.insumo

                if insumo.stock < item.cantidad:
                    messages.error(request, f"Stock insuficiente de {insumo.nombre}.")
                    return redirect("inventario:solicitud_detalle", pk=pk)

                insumo.stock -= item.cantidad
                insumo.save()

                Movimiento.objects.create(
                    insumo=insumo,
                    tipo="SALIDA",
                    cantidad=item.cantidad,
                    usuario=request.user,
                    observacion=f"Solicitud #{solicitud.id}"
                )

            solicitud.estado = "APROBADA"
            solicitud.save()
            messages.success(request, "Solicitud aprobada correctamente.")
            return redirect("inventario:solicitudes_listar")

        elif accion == "rechazar":
            solicitud.estado = "RECHAZADA"
            solicitud.observacion = request.POST.get("observacion", "")
            solicitud.save()

            messages.warning(request, "Solicitud rechazada.")
            return redirect("inventario:solicitudes_listar")

    return render(request, "inventario/solicitud_detalle.html", {
        "solicitud": solicitud,
        "items": items
    })

@login_required
@transaction.atomic
def solicitud_aprobar(request, pk):
    solicitud = get_object_or_404(SolicitudReposicion, pk=pk)

    if solicitud.estado != "PENDIENTE":
        messages.warning(request, "Esta solicitud ya fue procesada.")
        return redirect("inventario:solicitud_detalle", pk=pk)

    # Verificar stock
    for item in solicitud.items.all():
        if item.insumo.stock < item.cantidad:
            messages.error(request, f"No hay stock suficiente para {item.insumo.nombre}.")
            return redirect("inventario:solicitud_detalle", pk=pk)

    # Descontar stock y registrar movimiento
    for item in solicitud.items.all():
        insumo = item.insumo
        insumo.stock -= item.cantidad
        insumo.save()

        # Registrar movimiento en inventario
        Movimiento.objects.create(
            insumo=insumo,
            tipo="SALIDA",
            cantidad=item.cantidad,
            observacion=f"Solicitud aprobada #{solicitud.id} ({solicitud.area})"
        )

    solicitud.estado = "APROBADA"
    solicitud.save()

    messages.success(request, "Solicitud aprobada correctamente.")
    return redirect("inventario:solicitud_detalle", pk=pk)

@login_required
def solicitud_rechazar(request, pk):
    solicitud = get_object_or_404(SolicitudReposicion, pk=pk)

    if solicitud.estado != "PENDIENTE":
        messages.warning(request, "Esta solicitud ya fue procesada.")
        return redirect("inventario:solicitud_detalle", pk=pk)

    solicitud.estado = "RECHAZADA"
    solicitud.save()

    messages.success(request, "Solicitud rechazada.")
    return redirect("inventario:solicitud_detalle", pk=pk)