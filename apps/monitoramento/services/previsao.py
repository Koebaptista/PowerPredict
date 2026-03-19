import os
import joblib
import pandas as pd

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "ml_models", "modelo_consumo.pkl")

FEATURES = [
    "hora",
    "dia_semana",
    "temperatura",
    "mes",
    "fim_de_semana",
    "feriado",
    "consumo_base_estimado",
    "intensidade_operacional_local",
    "sensibilidade_temperatura_local",
]


def prever_consumo(
    hora,
    dia_semana,
    temperatura,
    mes,
    potencia_kw_ac_ref,
    fim_de_semana,
    feriado,
    consumo_base_estimado=None,
    intensidade_operacional_local=1.0,
    sensibilidade_temperatura_local=0.015,
):
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "Modelo não encontrado. Execute o treinamento antes de prever."
        )

    model = joblib.load(MODEL_PATH)

    if consumo_base_estimado is None:
        consumo_base_estimado = potencia_kw_ac_ref * 0.10

    entrada = pd.DataFrame([{
        "hora": hora,
        "dia_semana": dia_semana,
        "temperatura": temperatura,
        "mes": mes,
        "fim_de_semana": int(fim_de_semana),
        "feriado": int(feriado),
        "consumo_base_estimado": consumo_base_estimado,
        "intensidade_operacional_local": intensidade_operacional_local,
        "sensibilidade_temperatura_local": sensibilidade_temperatura_local,
    }])

    fator_utilizacao = float(model.predict(entrada)[0])
    fator_utilizacao = max(0.0, fator_utilizacao)

    consumo_kwh = fator_utilizacao * potencia_kw_ac_ref

    return {
        "fator_utilizacao": round(fator_utilizacao, 4),
        "potencia_kw_ac_ref": potencia_kw_ac_ref,
        "previsao_consumo_kwh": round(consumo_kwh, 4),
    }

def prever_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Recebe um DataFrame com as colunas necessárias e retorna
    o mesmo DataFrame com colunas adicionais:
      - fator_utilizacao_previsto
      - consumo_kwh_previsto
    """
    if not os.path.exists(MODEL_PATH):
        raise FileNotFoundError(
            "Modelo não encontrado. Execute o treinamento antes de analisar."
        )

    model = joblib.load(MODEL_PATH)

    df = df.copy()

    # Garante tipos corretos
    df["fim_de_semana"] = df["fim_de_semana"].astype(int)
    df["feriado"] = df["feriado"].astype(int)

    # consumo_base_estimado pode ser ausente no CSV novo
    if "consumo_base_estimado" not in df.columns:
        df["consumo_base_estimado"] = df["potencia_kw_ac_ref"] * 0.10

    if "intensidade_operacional_local" not in df.columns:
        df["intensidade_operacional_local"] = 1.0

    if "sensibilidade_temperatura_local" not in df.columns:
        df["sensibilidade_temperatura_local"] = 0.015

    X = df[FEATURES].copy()

    fatores = model.predict(X)
    fatores = [max(0.0, f) for f in fatores]

    df["fator_utilizacao_previsto"] = fatores
    df["consumo_kwh_previsto"] = [
        round(f * p, 4)
        for f, p in zip(fatores, df["potencia_kw_ac_ref"])
    ]

    return df