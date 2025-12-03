from django.db import models
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.models import User

# -------------------------
# INSUMOS MEDICOS
# -------------------------
class Insumo(models.Model):
    codigo = models.CharField(max_length=50, unique=True, blank=True)
    nombre = models.CharField(max_length=200)
    unidad = models.CharField(max_length=50)
    stock = models.IntegerField(default=0)
    stock_minimo = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.codigo:
            ultimo = Insumo.objects.order_by('-id').first()
            if ultimo and ultimo.codigo.startswith("INS-"):
                num = int(ultimo.codigo.split("-")[1]) + 1
            else:
                num = 1
            self.codigo = f"INS-{num:03d}"

        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"


# -------------------------
# FACTURAS DE INGRESO
# -------------------------
class FacturaIngreso(models.Model):

    TIPO_DTE = [
        (33, "Factura Electrónica (Afecta)"),
        (34, "Factura Exenta Electrónica"),
        (52, "Guía de Despacho"),
        (61, "Nota de Crédito"),
        (56, "Nota de Débito"),
    ]

    folio = models.PositiveIntegerField(unique=True)  # Número SII único
    tipo_dte = models.PositiveSmallIntegerField(choices=TIPO_DTE, default=33)

    fecha_emision = models.DateField()

    # Datos del proveedor (más realistas)
    proveedor_rut = models.CharField(max_length=15)  # Ej: 76.123.456-7
    proveedor_nombre = models.CharField(max_length=200)
    proveedor_giro = models.CharField(max_length=200, blank=True, null=True)

    # Usuario que registra en el sistema
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    # PDF opcional del DTE
    archivo_pdf = models.FileField(upload_to="facturas/", blank=True, null=True)

    def __str__(self):
        return f"DTE {self.folio} - {self.proveedor_nombre}"

    @property
    def subtotal_items(self):
        """Suma total de los items, útil si decides calcular neto automáticamente"""
        return sum(item.cantidad for item in self.items.all())


class ItemFactura(models.Model):
    factura = models.ForeignKey(
        FacturaIngreso,
        on_delete=models.CASCADE,
        related_name="items"
    )
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)

    cantidad = models.PositiveIntegerField()

    lote = models.CharField(max_length=100, blank=True, null=True)
    vencimiento = models.DateField(blank=True, null=True)

    @property
    def subtotal(self):
        return self.cantidad * self.precio_unitario

    def __str__(self):
        return f"{self.insumo.nombre} x {self.cantidad}"


# -------------------------
# MOVIMIENTOS DE INVENTARIO
# -------------------------
class Movimiento(models.Model):
    TIPO = [
        ("INGRESO", "Ingreso"),
        ("SALIDA", "Salida"),
        ("AJUSTE", "Ajuste")
    ]

    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    tipo = models.CharField(max_length=20, choices=TIPO)
    cantidad = models.IntegerField()
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(blank=True, null=True)
    factura = models.ForeignKey(FacturaIngreso, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.tipo} - {self.insumo} ({self.cantidad})"





def review_received(request, factura_id):
    factura = get_object_or_404(FacturaIngreso, id=factura_id)
    items = factura.items.all()

    if request.method == "POST":
        # Procesar cada item
        for item in items:
            recibido = int(request.POST.get(f"recibido_{item.id}", item.cantidad))
            obs = request.POST.get(f"obs_{item.id}", "")

            # Diferencias = discrepancias
            diferencia = recibido - item.cantidad

            # Registrar movimiento SI confirma
            if "confirmar" in request.POST:
                item.insumo.stock += recibido
                item.insumo.save()

                Movimiento.objects.create(
                    insumo=item.insumo,
                    tipo="INGRESO",
                    cantidad=recibido,
                    usuario=request.user,
                    factura=factura,
                    observacion=obs
                )

        messages.success(request, "Inventario actualizado correctamente.")
        return redirect("inventory_list")

    return render(request, "inventario/review_received.html", {
        "factura": factura,
        "items": items
    })