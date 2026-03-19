from django.db import models


class ConsumoEnergia(models.Model):
    nome = models.CharField(max_length=255)
    tipo_local = models.CharField(max_length=100)
    address = models.TextField(blank=True, null=True)

    data_hora = models.DateTimeField()

    ano = models.IntegerField()
    mes = models.IntegerField()
    dia = models.IntegerField()
    hora = models.IntegerField()
    dia_semana = models.IntegerField()

    fim_de_semana = models.BooleanField(default=False)
    feriado = models.BooleanField(default=False)

    temperatura = models.FloatField(null=True, blank=True)
    consumo_kwh = models.FloatField()

    anomalia = models.BooleanField(default=False)
    tipo_anomalia = models.CharField(max_length=50, default="normal")

    potencia_kw_ac_ref = models.FloatField()

    consumo_base_estimado = models.FloatField(null=True, blank=True)
    intensidade_operacional_local = models.FloatField(null=True, blank=True)
    sensibilidade_temperatura_local = models.FloatField(null=True, blank=True)

    def __str__(self):
        return f"{self.nome} - {self.data_hora} - {self.consumo_kwh}"