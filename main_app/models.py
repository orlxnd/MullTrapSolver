from django.db import models
from django.contrib.auth.models import User

class Historial(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    metodo = models.CharField(max_length=50)
    funcion = models.TextField()
    parametros = models.JSONField()
    resultado = models.TextField()
    pasos = models.TextField()
    fecha_creacion = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.usuario.username} - {self.metodo} - {self.fecha_creacion}'
