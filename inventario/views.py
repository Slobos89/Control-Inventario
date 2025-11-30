from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Insumo, FacturaIngreso, ItemFactura, Movimiento, SolicitudReposicion
from .forms import FacturaIngresoForm, ItemFacturaForm, SolicitudForm, UploadFileForm
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
    if request.method == "POST":
        factura_form = FacturaIngresoForm(request.POST)

        if factura_form.is_valid():
            factura = factura_form.save(commit=False)
            factura.usuario = request.user
            factura.save()

            # Capturar items dinámicos del form
            index = 1
            while True:
                insumo_key = f"insumo_{index}"
                cantidad_key = f"cantidad_{index}"
                lote_key = f"lote_{index}"
                venc_key = f"vencimiento_{index}"

                if insumo_key not in request.POST:
                    break  # no hay más items

                nombre_insumo = request.POST.get(insumo_key)
                cantidad = int(request.POST.get(cantidad_key))

                # buscar insumo o crearlo si no existe
                insumo, _ = Insumo.objects.get_or_create(
                    nombre=nombre_insumo,
                    defaults={"codigo": f"AUTO-{index}", "unidad": "unidad", "stock": 0, "stock_minimo": 0}
                )

                # registrar item de factura
                item = ItemFactura.objects.create(
                    factura=factura,
                    insumo=insumo,
                    cantidad=cantidad,
                    lote=request.POST.get(lote_key),
                    vencimiento=request.POST.get(venc_key) or None
                )

                # registrar movimiento
                Movimiento.objects.create(
                    insumo=insumo,
                    tipo="INGRESO",
                    cantidad=cantidad,
                    usuario=request.user,
                    factura=factura
                )

                # actualizar stock
                insumo.stock += cantidad
                insumo.save()

                index += 1

            messages.success(request, "Factura registrada correctamente.")
            return redirect("inventory_list")

    else:
        factura_form = FacturaIngresoForm()

    return render(request, "inventario/register_entry.html", {
        "form": factura_form,
    })


# ----------------------
# SOLICITUDES DE REPOSICIÓN
# ----------------------
@login_required
def requests_view(request):
    solicitudes = SolicitudReposicion.objects.all().order_by("-fecha")
    return render(request, "inventario/requests.html", {"solicitudes": solicitudes})


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
