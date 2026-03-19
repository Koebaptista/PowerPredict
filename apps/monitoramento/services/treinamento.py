import os
import json
import joblib
import pandas as pd

from datetime import datetime
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import train_test_split

from apps.monitoramento.models import ConsumoEnergia


BASE_DIR = os.path.dirname(os.path.dirname(__file__))
MODEL_DIR = os.path.join(BASE_DIR, "ml_models")
MODEL_PATH = os.path.join(MODEL_DIR, "modelo_consumo.pkl")
MODEL_INFO_PATH = os.path.join(MODEL_DIR, "modelo_consumo_info.json")

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

TARGET = "fator_utilizacao"


def treinar_modelo():
    total_banco = ConsumoEnergia.objects.count()
    print(f"[DEBUG] Total de registros no banco: {total_banco}")

    total_anomalia_false = ConsumoEnergia.objects.filter(anomalia=False).count()
    print(f"[DEBUG] Registros com anomalia=False: {total_anomalia_false}")

    total_anomalia_true = ConsumoEnergia.objects.filter(anomalia=True).count()
    print(f"[DEBUG] Registros com anomalia=True: {total_anomalia_true}")

    dados = list(ConsumoEnergia.objects.filter(anomalia=False).values())
    df = pd.DataFrame(dados)

    print(f"[DEBUG] Linhas carregadas do banco para DataFrame: {len(df)}")

    if df.empty:
        raise ValueError("Não existem dados no banco para treinar o modelo.")

    colunas_necessarias = FEATURES + ["consumo_kwh", "potencia_kw_ac_ref"]
    print(f"[DEBUG] Colunas disponíveis no DataFrame: {list(df.columns)}")
    print(f"[DEBUG] Colunas necessárias: {colunas_necessarias}")

    for coluna in colunas_necessarias:
        if coluna not in df.columns:
            raise ValueError(f"Coluna obrigatória ausente: {coluna}")

    antes_dropna = len(df)
    df = df.dropna(subset=colunas_necessarias)
    print(f"[DEBUG] Após dropna: {len(df)} linhas (removeu {antes_dropna - len(df)})")

    antes_potencia = len(df)
    df = df[df["potencia_kw_ac_ref"] > 0]
    print(f"[DEBUG] Após filtro potencia_kw_ac_ref > 0: {len(df)} linhas (removeu {antes_potencia - len(df)})")

    df[TARGET] = df["consumo_kwh"] / df["potencia_kw_ac_ref"]

    antes_target = len(df)
    df = df[(df[TARGET] >= 0) & (df[TARGET] <= 1.5)]
    print(f"[DEBUG] Após filtro do target entre 0 e 1.5: {len(df)} linhas (removeu {antes_target - len(df)})")

    if len(df) < 10:
        raise ValueError("Dados insuficientes após filtragem para treinar o modelo.")

    X = df[FEATURES].copy()
    y = df[TARGET].copy()

    X["fim_de_semana"] = X["fim_de_semana"].astype(int)
    X["feriado"] = X["feriado"].astype(int)

    print(f"[DEBUG] Shape de X: {X.shape}")
    print(f"[DEBUG] Shape de y: {y.shape}")

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    print(f"[DEBUG] Linhas em treino: {len(X_train)}")
    print(f"[DEBUG] Linhas em teste: {len(X_test)}")

    model = RandomForestRegressor(
        n_estimators=150,
        max_depth=18,
        min_samples_split=10,
        min_samples_leaf=4,
        random_state=42,
        n_jobs=-1,
    )

    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)

    mae = mean_absolute_error(y_test, y_pred)
    rmse = mean_squared_error(y_test, y_pred) ** 0.5
    r2 = r2_score(y_test, y_pred)

    print(f"[DEBUG] Métricas -> MAE: {mae:.6f} | RMSE: {rmse:.6f} | R2: {r2:.6f}")

    os.makedirs(MODEL_DIR, exist_ok=True)
    joblib.dump(model, MODEL_PATH)

    importancias = {
        nome: float(valor)
        for nome, valor in zip(FEATURES, model.feature_importances_)
    }

    info_modelo = {
        "modelo": type(model).__name__,
        "data_treinamento": datetime.now().isoformat(),
        "total_registros": int(len(df)),
        "qtd_treino": int(len(X_train)),
        "qtd_teste": int(len(X_test)),
        "features": FEATURES,
        "target": TARGET,
        "nota_target": (
            "O modelo prevê o fator de utilização (consumo / potencia_instalada). "
            "Para obter kWh, multiplique o resultado pela potencia_kw_ac_ref do local."
        ),
        "importancia_das_features": importancias,
        "metricas": {
            "mae": float(mae),
            "rmse": float(rmse),
            "r2": float(r2),
            "interpretacao": (
                "Métricas calculadas sobre o fator de utilização, não sobre kWh diretamente."
            ),
        },
    }

    with open(MODEL_INFO_PATH, "w", encoding="utf-8") as f:
        json.dump(info_modelo, f, ensure_ascii=False, indent=4)

    return {
        "mensagem": "Modelo treinado com sucesso.",
        "arquivo_modelo": MODEL_PATH,
        "arquivo_info": MODEL_INFO_PATH,
        "total_registros": len(df),
        "metricas": info_modelo["metricas"],
        "features": FEATURES,
        "target": TARGET,
    }