import os
import json

BASE_DIR        = os.path.dirname(os.path.dirname(__file__))
MODEL_INFO_PATH = os.path.join(BASE_DIR, "ml_models", "modelo_consumo_info.json")


def obter_info_modelo():
    if not os.path.exists(MODEL_INFO_PATH):
        raise FileNotFoundError(
            "Arquivo de informações do modelo não encontrado. "
            "Treine o modelo primeiro."
        )

    with open(MODEL_INFO_PATH, "r", encoding="utf-8") as f:
        info = json.load(f)

    return info