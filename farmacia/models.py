from django.db import models
from django.contrib.auth.models import User
from inventario.models import Insumo

class Medicamento(models.Model):
    codigo = models.CharField(max_length=50, unique=True, blank=True)
    nombre = models.CharField(max_length=200)
    descripcion = models.TextField(blank=True)
    lote = models.CharField(max_length=100, blank=True, null=True)
    fecha_vencimiento = models.DateField(blank=True, null=True)
    stock = models.IntegerField(default=0)
    stock_critico = models.IntegerField(default=0)

    def save(self, *args, **kwargs):
        if not self.codigo:
            ultimo = Medicamento.objects.order_by('-id').first()
            if ultimo and ultimo.codigo.startswith("MED-"):
                num = int(ultimo.codigo.split("-")[1]) + 1
            else:
                num = 1
            self.codigo = f"MED-{num:03d}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.codigo} - {self.nombre}"

class MovimientoFarmacia(models.Model):
    TIPO = (("INGRESO", "Ingreso"), ("SALIDA", "Salida"), ("AJUSTE", "Ajuste"))
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE, related_name="movimientos")
    tipo = models.CharField(max_length=10, choices=TIPO)
    cantidad = models.IntegerField()
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    observacion = models.TextField(blank=True, null=True)
    factura = models.ForeignKey("FacturaFarmacia", on_delete=models.SET_NULL,null=True, blank=True, related_name="movimientos")

    def __str__(self):
        return f"{self.tipo} - {self.medicamento} {self.cantidad}"

# -------------------------
# SOLICITUDES DE REPOSICIÓN
# -------------------------
class SolicitudReposicion(models.Model):
    ESTADO = [
        ("PENDIENTE", "Pendiente"),
        ("APROBADA", "Aprobada"),
        ("RECHAZADA", "Rechazada"),
    ]

    area = models.CharField(max_length=200)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha = models.DateTimeField(auto_now_add=True)
    estado = models.CharField(max_length=20, choices=ESTADO, default="PENDIENTE")
    observacion = models.TextField(blank=True, null=True)  # opcional

    def __str__(self):
        return f"Solicitud {self.id} - {self.area}"

    @property
    def total_items(self):
        return self.items.count()

    @property
    def esta_pendiente(self):
        return self.estado == "PENDIENTE"


class ItemSolicitud(models.Model):
    solicitud = models.ForeignKey(
        SolicitudReposicion,
        on_delete=models.CASCADE,
        related_name="items"
    )
    insumo = models.ForeignKey(Insumo, on_delete=models.CASCADE)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.insumo.nombre} x {self.cantidad}"

class FacturaFarmacia(models.Model):

    TIPO_DTE = [
        (33, "Factura Electrónica (Afecta)"),
        (34, "Factura Exenta Electrónica"),
        (52, "Guía de Despacho"),
        (61, "Nota de Crédito"),
        (56, "Nota de Débito"),
    ]

    # Número de foliación (folio del SII)
    folio = models.PositiveIntegerField()

    tipo_dte = models.PositiveSmallIntegerField(choices=TIPO_DTE, default=33)

    fecha_emision = models.DateField()

    # Datos del proveedor
    proveedor_rut = models.CharField(max_length=15)      # Ej: 76.123.456-7
    proveedor_nombre = models.CharField(max_length=200)
    proveedor_giro = models.CharField(max_length=200, blank=True, null=True)

    # Usuario registrador
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    fecha_registro = models.DateTimeField(auto_now_add=True)

    # PDF opcional del DTE
    archivo_pdf = models.FileField(upload_to="facturas_farmacia/", blank=True, null=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["folio", "proveedor_rut"],
                name="unique_folio_por_proveedor"
            )
        ]

    def __str__(self):
        return f"DTE {self.folio} - {self.proveedor_nombre}"

    @property
    def total_items(self):
        """Devuelve la suma de todas las cantidades ingresadas en el detalle."""
        return sum(item.cantidad for item in self.items.all())

class ItemFacturaFarmacia(models.Model):
    factura = models.ForeignKey(FacturaFarmacia, on_delete=models.CASCADE, related_name="items")
    medicamento = models.ForeignKey(Medicamento, on_delete=models.PROTECT)
    lote = models.CharField(max_length=100)
    vencimiento = models.DateField(null=True, blank=True)
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.medicamento.nombre} x {self.cantidad}"

class Dispensacion(models.Model):
    receta = models.CharField(max_length=100)
    paciente_rut = models.CharField(max_length=20)
    medicamento = models.ForeignKey(Medicamento, on_delete=models.PROTECT)
    cantidad = models.PositiveIntegerField()
    fecha = models.DateTimeField(auto_now_add=True)
    usuario = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    observacion = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"Dispensación {self.receta} - {self.medicamento.nombre}"

class LoteFarmacia(models.Model):
    medicamento = models.ForeignKey(Medicamento, on_delete=models.CASCADE)
    lote = models.CharField(max_length=100)
    vencimiento = models.DateField()
    cantidad = models.PositiveIntegerField()

    def __str__(self):
        return f"{self.medicamento.nombre} - Lote {self.lote} ({self.cantidad})"