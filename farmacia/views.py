from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.encoding import smart_str
from itertools import zip_longest
from .models import *
from .forms import *
from datetime import datetime
import csv


# helper permission check
def rol_permitido(user, allowed):
    try:
        return user.is_authenticated and user.perfil.rol in allowed
    except Exception:
        return False

@login_required
def lista_medicamentos(request):
    if not rol_permitido(request.user, ["ADMIN","JEFE_FARMACIA","FUNC_FARMACIA"]):
        messages.error(request, "No tienes permiso para ver inventario de farmacia.")
        return redirect("index")
    meds = Medicamento.objects.all().order_by('nombre')
    return render(request, "farmacia/medicamento_list.html", {"medicamentos": meds})

@login_required
def detalle_medicamento(request, pk):
    medicamento = get_object_or_404(Medicamento, pk=pk)

    # Últimos movimientos
    movimientos = MovimientoFarmacia.objects.filter(
        medicamento=medicamento
    ).order_by("-fecha")[:10]

    # ---- ALERTAS DE VENCIMIENTO ----
    hoy = date.today()
    en_30 = hoy + timedelta(days=30)
    en_60 = hoy + timedelta(days=60)

    # Lotes asociados al medicamento
    lotes = ItemFactura.objects.filter(medicamento=medicamento)

    # Lotes que vencen en <30 días
    vencen_menos_30 = lotes.filter(
        vencimiento__isnull=False,
        vencimiento__gte=hoy,
        vencimiento__lte=en_30,
    ).count()

    # Lotes que vencen entre 30 y 60 días
    vencen_30_60 = lotes.filter(
        vencimiento__isnull=False,
        vencimiento__gt=en_30,
        vencimiento__lte=en_60,
    ).count()

    context = {
        "medicamento": medicamento,
        "movimientos": movimientos,
        "vencen_menos_30": vencen_menos_30,
        "vencen_30_60": vencen_30_60,
    }

    return render(request, "farmacia/detalle_medicamento.html", context)

@login_required
def crear_medicamento(request):
    if not rol_permitido(request.user, ["ADMIN","JEFE_FARMACIA"]):
        messages.error(request, "No tienes permiso para crear medicamentos.")
        return redirect("farmacia/medicamento_list.html")
    if request.method == "POST":
        form = MedicamentoForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Medicamento creado.")
            return redirect("farmacia/medicamento_list.html")
    else:
        form = MedicamentoForm()
    return render(request, "farmacia/medicamento_form.html", {"form": form})

@login_required
def movimiento_crear(request):
    if not rol_permitido(request.user, ["ADMIN","JEFE_FARMACIA","FUNC_FARMACIA"]):
        messages.error(request, "No tienes permiso para registrar movimientos.")
        return redirect("farmacia/medicamento_list.html")

    if request.method == "POST":
        form = MovimientoFarmaciaForm(request.POST)
        if form.is_valid():
            mov = form.save(commit=False)
            mov.usuario = request.user
            mov.save()

            # actualizar stock
            med = mov.medicamento
            if mov.tipo == "INGRESO":
                med.stock += mov.cantidad
            elif mov.tipo == "SALIDA":
                med.stock -= mov.cantidad
            elif mov.tipo == "AJUSTE":
                med.stock = mov.cantidad  # si se usa ajuste absoluto (ajustar conforme política)
            med.save()

            messages.success(request, "Movimiento registrado.")
            return redirect("farmacia:detalle", pk=med.pk)
    else:
        form = MovimientoFarmaciaForm()
    return render(request, "farmacia/movimiento_form.html", {"form": form})

def dispense(request):
    return render(request, "farmacia/dispense.html")


@login_required
def import_inventory_farmacia(request):

    # Permisos
    if not request.user.is_authenticated or request.user.perfil.rol not in ["ADMIN", "JEFE_FARMACIA"]:
        messages.error(request, "No tienes permiso para importar inventario.")
        return redirect("farmacia:medicamentos_lista")

    # -------------------------------------
    # GET → mostrar formulario
    # -------------------------------------
    if request.method == "GET":
        return render(request, "farmacia/import_inventory.html")

    # -------------------------------------
    # POST → procesar archivo
    # -------------------------------------
    if "archivo" not in request.FILES:
        messages.error(request, "Debes subir un archivo CSV.")
        return redirect("farmacia:import_inventory")

    file = request.FILES.get("archivo")

    # Intentar decodificar CSV
    try:
        decoded = file.read().decode("utf-8")
    except UnicodeDecodeError:
        decoded = file.read().decode("latin-1")

    # Separar líneas
    lineas = decoded.splitlines()

    if not lineas:
        messages.error(request, "El archivo está vacío.")
        return redirect("farmacia:import_inventory")

    # -------------------------------------
    # PROCESAR ENCABEZADOS
    # -------------------------------------
    raw_headers = lineas[0].replace(",", ";").split(";")
    headers = [h.strip().lower() for h in raw_headers]

    requeridos = ["nombre", "stock", "vencimiento"]

    if headers != requeridos:
        messages.error(
            request,
            f"ENCABEZADOS CSV INCORRECTOS: {headers}. Debe ser exactamente: {requeridos}"
        )
        return redirect("farmacia:import_inventory")

    creados = 0
    actualizados = 0

    # -------------------------------------
    # PROCESAR FILAS DEL CSV
    # -------------------------------------
    for linea in lineas[1:]:
        if not linea.strip():
            continue  # saltar líneas vacías

        partes = linea.replace(",", ";").split(";")

        if len(partes) != 3:
            continue  # saltar líneas mal formadas

        row = dict(zip(headers, partes))

        nombre = row["nombre"].strip()
        stock = int(row["stock"].strip())
        venc_raw = row["vencimiento"].strip()

        # -------------------------
        # CONVERSIÓN DE FECHA
        # -------------------------
        venc = None
        if venc_raw:
            formatos = ["%d/%m/%Y", "%d-%m-%Y", "%Y-%m-%d"]
            for fmt in formatos:
                try:
                    venc = datetime.strptime(venc_raw, fmt).date()
                    break
                except ValueError:
                    continue

            if venc is None:
                messages.error(request, f"Fecha inválida en: {venc_raw}. Usa DD/MM/YYYY o YYYY-MM-DD.")
                return redirect("farmacia:import_inventory")

        # -------------------------
        # CREAR O ACTUALIZAR
        # -------------------------
        med, creado = Medicamento.objects.get_or_create(
            nombre=nombre,
            defaults={
                "stock": stock,
                "fecha_vencimiento": venc
            }
        )

        if creado:
            creados += 1
        else:
            med.stock = stock
            med.fecha_vencimiento = venc
            med.save()
            actualizados += 1

    # -------------------------------------
    # RESULTADO
    # -------------------------------------
    messages.success(
        request,
        f"Importación completada: {creados} medicamentos creados, {actualizados} actualizados."
    )

    return redirect("farmacia:medicamentos_lista")

@login_required
def dispensar_medicamento(request):
    if request.method == "POST":
        form = DispensacionForm(request.POST)

        if form.is_valid():
            medicamento = form.cleaned_data["medicamento"]
            cantidad = form.cleaned_data["cantidad"]
            observacion = form.cleaned_data["observacion"]

            # Validar stock
            if cantidad > medicamento.stock:
                messages.error(request, f"No hay suficiente stock. Disponible: {medicamento.stock}")
                return redirect("dispensar_medicamento")

            # Restar stock
            medicamento.stock -= cantidad
            medicamento.save()

            # Registrar movimiento
            MovimientoFarmacia.objects.create(
                medicamento=medicamento,
                tipo="SALIDA",
                cantidad=cantidad,
                usuario=request.user,
                observacion=observacion
            )

            messages.success(request, "Medicamento dispensado correctamente.")
            return redirect("dispensar_medicamento")
    else:
        form = DispensacionForm()

    return render(request, "farmacia/dispense.html", {"form": form})

# ----------------------
# SOLICITUDES DE REPOSICIÓN
# ----------------------
@login_required
def solicitud_crear(request):

    if request.method == "POST":

        area = request.POST.get("area")
        solicitud = SolicitudReposicion.objects.create(
            usuario=request.user,
            area=area
        )

        index = 1
        while True:
            insumo_key = f"insumo_{index}"
            cantidad_key = f"cantidad_{index}"

            if insumo_key not in request.POST:
                break

            insumo_id = request.POST.get(insumo_key)
            if not insumo_id:
                index += 1
                continue

            cantidad = int(request.POST.get(cantidad_key, 0))

            insumo = get_object_or_404(Insumo, pk=insumo_id)

            ItemSolicitud.objects.create(
                solicitud=solicitud,
                insumo=insumo,
                cantidad=cantidad
            )

            index += 1

        messages.success(request, "Solicitud creada correctamente.")
        return redirect("farmacia:solicitudes_mias")

    insumos = Insumo.objects.all().order_by("nombre")
    return render(request, "farmacia/solicitud_crear.html", {"insumos": insumos})

@login_required
def solicitudes_mias(request):
    solicitudes = SolicitudReposicion.objects.filter(usuario=request.user).order_by("-fecha")
    return render(request, "farmacia/solicitudes_mias.html", {"solicitudes": solicitudes})

@login_required
def crear_factura_farmacia(request):

    medicamentos = Medicamento.objects.all().order_by("nombre")

    if request.method == "POST":
        factura_form = FacturaFarmaciaForm(request.POST)

        if factura_form.is_valid():
            factura = factura_form.save(commit=False)
            factura.usuario = request.user
            factura.save()

            index = 1
            while True:

                # Nombres esperados en el POST
                medicamento_key = f"medicamento_{index}"
                cantidad_key = f"cantidad_{index}"
                lote_key = f"lote_{index}"
                venc_key = f"vencimiento_{index}"

                # Si no existe, terminamos
                if medicamento_key not in request.POST:
                    break

                medicamento_id = request.POST.get(medicamento_key)

                # Si estaba la key pero vacía → seguimos
                if not medicamento_id:
                    index += 1
                    continue

                cantidad = int(request.POST.get(cantidad_key, 0))
                lote = request.POST.get(lote_key)
                venc = request.POST.get(venc_key)

                # Convertimos fecha
                if venc:
                    from datetime import datetime
                    venc = datetime.strptime(venc, "%Y-%m-%d").date()

                med = get_object_or_404(Medicamento, pk=medicamento_id)

                # Crear item factura
                item = ItemFacturaFarmacia.objects.create(
                    factura=factura,
                    medicamento=med,
                    lote=lote,
                    vencimiento=venc,
                    cantidad=cantidad
                )

                # Crear lote para control de vencimiento
                LoteFarmacia.objects.create(
                    medicamento=med,
                    lote=lote,
                    vencimiento=venc,
                    cantidad=cantidad
                )

                # Movimiento
                MovimientoFarmacia.objects.create(
                    medicamento=med,
                    tipo="INGRESO",
                    cantidad=cantidad,
                    usuario=request.user,
                    factura=factura,
                    observacion=f"Ingreso por factura {factura.folio}"
                )

                # Actualizar stock
                med.stock += cantidad
                med.save()

                index += 1

            messages.success(request, "Factura registrada correctamente.")
            return redirect("farmacia:facturas_list")

        else:
            messages.error(request, "Corrige los errores del formulario.")

    else:
        factura_form = FacturaFarmaciaForm()

    return render(request, "farmacia/crear_factura.html", {
        "form": factura_form,
        "medicamentos": medicamentos,
    })


    
def factura_farmacia_detalle(request, pk):
    factura = get_object_or_404(FacturaFarmacia, pk=pk)
    items = factura.items.all()

    return render(request, "farmacia/factura_detalle.html", {
        "factura": factura,
        "items": items
    })

def facturas_farmacia_list(request):
    facturas = FacturaFarmacia.objects.order_by("-fecha_emision")

    return render(request, "farmacia/facturas_list.html", {
        "facturas": facturas
    })

@login_required
def dispense(request):
    if not rol_permitido(request.user, ["JEFE_FARMACIA", "FUNC_FARMACIA"]):
        messages.error(request, "No tienes permiso para dispensar medicamentos.")
        return redirect("index")

    medicamentos = Medicamento.objects.all().order_by("nombre")

    if request.method == "POST":
        receta = request.POST.get("receta_num")
        paciente = request.POST.get("rut_paciente")

        lista_meds = request.POST.getlist("medicamento[]")
        lista_cants = request.POST.getlist("cantidad[]")
        lista_obs = request.POST.getlist("observacion[]")

        # Validación básica
        if not receta or not paciente:
            messages.error(request, "Debe ingresar receta y RUT.")
            return redirect("farmacia:dispense")

        # Iteramos cada fila
        for med_id, cant, obs in zip_longest(lista_meds, lista_cants, lista_obs, fillvalue=""):

            if not med_id or not cant:
                continue  # Fila incompleta

            medicamento = Medicamento.objects.get(id=med_id)
            cant = int(cant)

            # Validación stock
            if cant > medicamento.stock:
                messages.error(request, f"Stock insuficiente para {medicamento.nombre}. Disponible: {medicamento.stock}")
                return redirect("farmacia:dispense")

            # Crear dispensación
            d = Dispensacion.objects.create(
                receta=receta,
                paciente_rut=paciente,
                medicamento=medicamento,
                cantidad=cant,
                observacion=obs,
                usuario=request.user,
            )

            # Descontar stock
            medicamento.stock -= cant
            medicamento.save()

            # Registrar movimiento
            MovimientoFarmacia.objects.create(
                medicamento=medicamento,
                tipo="SALIDA",
                cantidad=cant,
                usuario=request.user,
                observacion=f"Dispensación receta {receta}"
            )

        messages.success(request, "Dispensación registrada correctamente.")
        return redirect("farmacia:dispense")

    return render(request, "farmacia/dispense.html", {
        "medicamentos": medicamentos
    })

@login_required
def dispensaciones_list(request):

    if not rol_permitido(request.user, ["JEFE_FARMACIA", "FUNC_FARMACIA"]):
        messages.error(request, "No tienes permiso para ver dispensaciones.")
        return redirect("index")

    dispensaciones = Dispensacion.objects.all().order_by("-fecha")

    return render(request, "farmacia/dispensaciones_list.html", {
        "dispensaciones": dispensaciones
    })

@login_required
def dispensacion_detail(request, id):
    if not rol_permitido(request.user, ["JEFE_FARMACIA", "FUNC_FARMACIA"]):
        messages.error(request, "No tienes permiso para ver dispensaciones.")
        return redirect("index")

    d = get_object_or_404(Dispensacion, id=id)

    return render(request, "farmacia/dispensacion_detail.html", {"d": d})