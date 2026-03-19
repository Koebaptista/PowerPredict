import pandas as pd
from sklearn.ensemble import IsolationForest
from apps.monitoramento.models import ConsumoEnergia

FEATURES = [
    "fator_utilizacao",
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


def detectar_anomalias():
    dados = list(
        ConsumoEnergia.objects.all().values(
            "id",
            "consumo_kwh",
            "potencia_kw_ac_ref",
            "hora",
            "dia_semana",
            "temperatura",
            "mes",
            "fim_de_semana",
            "feriado",
            "consumo_base_estimado",
            "intensidade_operacional_local",
            "sensibilidade_temperatura_local",
        )
    )
    df = pd.DataFrame(dados)

    if df.empty:
        raise ValueError("Não há dados para detectar anomalias.")

    colunas_necessarias = [
        "consumo_kwh",
        "potencia_kw_ac_ref",
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

    df = df[df["potencia_kw_ac_ref"] > 0].copy()
    df = df.dropna(subset=colunas_necessarias)

    df["fator_utilizacao"] = df["consumo_kwh"] / df["potencia_kw_ac_ref"]

    df_modelo = df[FEATURES].copy()
    df_modelo["fim_de_semana"] = df_modelo["fim_de_semana"].astype(int)
    df_modelo["feriado"] = df_modelo["feriado"].astype(int)

    modelo = IsolationForest(
        contamination=0.02,
        random_state=42,
        n_estimators=200,
        n_jobs=-1,
    )

    resultado = modelo.fit_predict(df_modelo)
    df["anomalia"] = [r == -1 for r in resultado]

    objs = []
    for row in df[["id", "anomalia"]].itertuples(index=False):
        objs.append(
            ConsumoEnergia(
                id=row.id,
                anomalia=bool(row.anomalia),
            )
        )

    ConsumoEnergia.objects.bulk_update(objs, ["anomalia"], batch_size=1000)

    total_anomalias = int(df["anomalia"].sum())

    return {
        "mensagem": "Detecção de anomalias concluída.",
        "total_registros": len(df),
        "anomalias_encontradas": total_anomalias,
        "percentual": round(total_anomalias / len(df) * 100, 2),
    }


def detectar_anomalias_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica IsolationForest diretamente em um DataFrame já com
    fator_utilizacao_previsto calculado (ou consumo_kwh + potencia_kw_ac_ref).
    Adiciona coluna: anomalia_csv (bool)
    """
    df = df.copy()

    # calcula fator se ainda não existir
    if "fator_utilizacao" not in df.columns:
        if "consumo_kwh" in df.columns and "potencia_kw_ac_ref" in df.columns:
            df["fator_utilizacao"] = (
                df["consumo_kwh"] / df["potencia_kw_ac_ref"].replace(0, pd.NA)
            ).fillna(0)
        elif "fator_utilizacao_previsto" in df.columns:
            df["fator_utilizacao"] = df["fator_utilizacao_previsto"]
        else:
            df["fator_utilizacao"] = 0.0

    colunas_modelo = [c for c in FEATURES if c in df.columns]

    df_modelo = df[colunas_modelo].copy()
    df_modelo["fim_de_semana"] = df_modelo["fim_de_semana"].astype(int)
    df_modelo["feriado"] = df_modelo["feriado"].astype(int)
    df_modelo = df_modelo.fillna(0)

    modelo_iso = IsolationForest(
        contamination=0.02,
        random_state=42,
        n_estimators=200,
        n_jobs=-1,
    )

    resultado = modelo_iso.fit_predict(df_modelo)
    df["anomalia_csv"] = [r == -1 for r in resultado]

    return df