from rest_framework import serializers
from .models import ConsumoEnergia

class ConsumoSerializer(serializers.ModelSerializer):

    class Meta:
        model = ConsumoEnergia
        fields = "__all__"