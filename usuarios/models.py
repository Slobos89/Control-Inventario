from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

class Perfil(models.Model):
    ROLES = [
        ('ADMIN', 'Administrador'),
        ('JEFE_BODEGA', 'Jefe de Bodega'),
        ('FUNC_BODEGA', 'Funcionario Bodega'),
        ('JEFE_FARMACIA', 'Jefe de Farmacia'),
        ('FUNC_FARMACIA', 'Funcionario Farmacia'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    rol = models.CharField(max_length=20, choices=ROLES)

    def __str__(self):
        return f"{self.user.username} - {self.get_rol_display()}"

@receiver(post_save, sender=User)
def crear_perfil(sender, instance, created, **kwargs):
    if created:
        Perfil.objects.create(user=instance)

@receiver(post_save, sender=User)
def guardar_perfil(sender, instance, **kwargs):
    instance.perfil.save()