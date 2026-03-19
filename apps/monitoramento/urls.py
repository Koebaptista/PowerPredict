from django.urls import path
from .views import (
    listar_consumo,
    upload_dataset_api,
    treinar_modelo_api,
    prever_consumo_api,
    detectar_anomalias_api,
    listar_anomalias,
    info_modelo_api,
    analisar_csv_api,
    limpar_base_api,
)

urlpatterns = [
    path("consumo/", listar_consumo),
    path("upload/", upload_dataset_api),
    path("analisar-csv/",  analisar_csv_api),
    path("modelo/treinar/", treinar_modelo_api),
    path("prever/", prever_consumo_api),
    path("anomalias/", listar_anomalias),
    path("detectar-anomalias/", detectar_anomalias_api),
    path("modelo-info/", info_modelo_api),
    path("analisar-csv/", analisar_csv_api),
    path("limpar-base/", limpar_base_api),
    
]