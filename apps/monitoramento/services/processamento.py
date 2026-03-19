import pandas as pd
from apps.monitoramento.models import ConsumoEnergia


def carregar_dados_dataframe():
    dados = list(ConsumoEnergia.objects.all().values())
    df = pd.DataFrame(dados)

    if df.empty:
        return df

    df["data_hora"] = pd.to_datetime(df["data_hora"])

    if "temperatura" in df.columns:
        df["temperatura"] = df["temperatura"].fillna(df["temperatura"].mean())

    return df