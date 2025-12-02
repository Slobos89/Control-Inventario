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

    def __str__(self):
        return f"{self.tipo} {self.cantidad} - {self.medicamento}"

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