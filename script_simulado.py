import pandas as pd
import random
from datetime import datetime, timedelta

# ─────────────────────────────────────────────
# CONFIGURAÇÕES GERAIS
# ─────────────────────────────────────────────
ARQUIVO_ENTRADA = "Solar_On_City_Facilities.csv"
ARQUIVO_SAIDA   = "dados_simulados_consumo.csv"
DATA_INICIO     = datetime(2025, 1, 1)
DIAS            = 365

SEED = 42
random.seed(SEED)

# feriados simples para simulação
FERIADOS_FIXOS = {
    "01-01",  # ano novo
    "04-21",  # tiradentes
    "05-01",  # trabalho
    "09-07",  # independência
    "10-12",  # nossa senhora
    "11-02",  # finados
    "11-15",  # proclamação
    "12-25",  # natal
}


# ─────────────────────────────────────────────
# CLASSIFICAÇÃO DO TIPO DE LOCAL
# ─────────────────────────────────────────────
def classificar_tipo(nome: str) -> str:
    nome = str(nome).lower()

    if "library" in nome:
        return "biblioteca"
    elif "health" in nome or "hospital" in nome or "clinic" in nome:
        return "instalacao_saude"
    elif "airport" in nome:
        return "aeroporto"
    elif "cinema" in nome or "theater" in nome or "theatre" in nome:
        return "cinema"
    elif "school" in nome or "education" in nome:
        return "educacao"
    elif "office" in nome or "administration" in nome or "service center" in nome:
        return "administrativo"

    return "geral"


# ─────────────────────────────────────────────
# PERFIL INDIVIDUAL POR INSTALAÇÃO
# ─────────────────────────────────────────────
def gerar_perfil_local(nome: str, tipo: str, potencia: float) -> dict:
    """
    Cria uma 'personalidade' fixa para cada instalação.
    Isso evita que dois locais do mesmo tipo fiquem iguais demais.
    """

    # base mínima sempre ligada
    if tipo == "biblioteca":
        consumo_base_pct = random.uniform(0.04, 0.10)
        sens_temp = random.uniform(0.010, 0.020)
        intensidade = random.uniform(0.85, 1.10)
        abertura_offset = random.choice([-1, 0, 1])
        fechamento_offset = random.choice([-1, 0, 1])

    elif tipo == "instalacao_saude":
        consumo_base_pct = random.uniform(0.18, 0.35)
        sens_temp = random.uniform(0.012, 0.022)
        intensidade = random.uniform(0.90, 1.20)
        abertura_offset = 0
        fechamento_offset = 0

    elif tipo == "aeroporto":
        consumo_base_pct = random.uniform(0.25, 0.45)
        sens_temp = random.uniform(0.015, 0.028)
        intensidade = random.uniform(0.95, 1.25)
        abertura_offset = 0
        fechamento_offset = 0

    elif tipo == "cinema":
        consumo_base_pct = random.uniform(0.08, 0.18)
        sens_temp = random.uniform(0.015, 0.030)
        intensidade = random.uniform(0.90, 1.25)
        abertura_offset = random.choice([-1, 0, 1, 2])
        fechamento_offset = random.choice([0, 1, 2])

    elif tipo == "educacao":
        consumo_base_pct = random.uniform(0.05, 0.12)
        sens_temp = random.uniform(0.010, 0.020)
        intensidade = random.uniform(0.85, 1.15)
        abertura_offset = random.choice([-1, 0, 1])
        fechamento_offset = random.choice([-1, 0, 1])

    elif tipo == "administrativo":
        consumo_base_pct = random.uniform(0.06, 0.14)
        sens_temp = random.uniform(0.010, 0.022)
        intensidade = random.uniform(0.85, 1.10)
        abertura_offset = random.choice([-1, 0, 1])
        fechamento_offset = random.choice([-1, 0, 1])

    else:
        consumo_base_pct = random.uniform(0.06, 0.18)
        sens_temp = random.uniform(0.010, 0.025)
        intensidade = random.uniform(0.85, 1.15)
        abertura_offset = random.choice([-1, 0, 1])
        fechamento_offset = random.choice([-1, 0, 1])

    return {
        "consumo_base_pct": round(consumo_base_pct, 4),
        "sens_temp": round(sens_temp, 4),
        "intensidade": round(intensidade, 4),
        "abertura_offset": abertura_offset,
        "fechamento_offset": fechamento_offset,
        "potencia": potencia,
        "nome": nome,
        "tipo": tipo,
    }


# ─────────────────────────────────────────────
# FERIADO
# ─────────────────────────────────────────────
def eh_feriado(data_atual: datetime) -> int:
    chave = data_atual.strftime("%m-%d")
    return 1 if chave in FERIADOS_FIXOS else 0


# ─────────────────────────────────────────────
# FATOR HORÁRIO POR TIPO + PERFIL DO LOCAL
# ─────────────────────────────────────────────
def fator_horario(hora: int, tipo: str, perfil: dict) -> float:
    abertura_offset = perfil["abertura_offset"]
    fechamento_offset = perfil["fechamento_offset"]

    if tipo == "biblioteca":
        inicio_baixo = 5 + abertura_offset
        inicio_pico  = 8 + abertura_offset
        fim_pico     = 17 + fechamento_offset
        fim_medio    = 21 + fechamento_offset

        if hora <= max(0, inicio_baixo):
            return 0.20
        if hora <= max(0, inicio_pico):
            return 0.50
        if hora <= min(23, fim_pico):
            return 0.92
        if hora <= min(23, fim_medio):
            return 0.52
        return 0.30

    if tipo == "instalacao_saude":
        if hora <= 5:
            return 0.68
        if hora <= 17:
            return 0.88
        return 0.76

    if tipo == "aeroporto":
        if hora <= 5:
            return 0.75
        if hora <= 22:
            return 0.98
        return 0.84

    if tipo == "cinema":
        abertura = 10 + abertura_offset
        pre_pico = 13 + abertura_offset
        pico     = 23 + fechamento_offset

        if hora <= max(0, abertura):
            return 0.15
        if hora <= max(0, pre_pico):
            return 0.45
        if hora <= min(23, pico):
            return 0.98
        return 0.18

    if tipo == "educacao":
        if hora <= 5:
            return 0.18
        if hora <= 7 + abertura_offset:
            return 0.45
        if hora <= 17 + fechamento_offset:
            return 0.95
        if hora <= 21:
            return 0.35
        return 0.20

    if tipo == "administrativo":
        if hora <= 5:
            return 0.15
        if hora <= 8 + abertura_offset:
            return 0.45
        if hora <= 18 + fechamento_offset:
            return 0.88
        return 0.25

    if hora <= 5:
        return 0.30
    if hora <= 17:
        return 0.80
    return 0.50


# ─────────────────────────────────────────────
# FATOR DIA DA SEMANA
# ─────────────────────────────────────────────
def fator_dia_semana(dia: int, tipo: str) -> float:
    fim_de_semana = dia >= 5

    if tipo == "biblioteca":
        return 0.35 if fim_de_semana else 1.0

    if tipo == "instalacao_saude":
        return 0.90 if fim_de_semana else 1.0

    if tipo == "aeroporto":
        return 1.08 if fim_de_semana else 1.0

    if tipo == "cinema":
        if dia == 4:
            return 1.10
        if dia == 5:
            return 1.28
        if dia == 6:
            return 1.18
        if dia <= 1:
            return 0.60
        return 0.78

    if tipo == "educacao":
        return 0.15 if fim_de_semana else 1.0

    if tipo == "administrativo":
        return 0.25 if fim_de_semana else 1.0

    return 0.55 if fim_de_semana else 1.0


# ─────────────────────────────────────────────
# FATOR FERIADO
# ─────────────────────────────────────────────
def fator_feriado(tipo: str, feriado: int) -> float:
    if not feriado:
        return 1.0

    if tipo == "biblioteca":
        return 0.15
    if tipo == "instalacao_saude":
        return 0.95
    if tipo == "aeroporto":
        return 1.10
    if tipo == "cinema":
        return 1.20
    if tipo == "educacao":
        return 0.08
    if tipo == "administrativo":
        return 0.10

    return 0.40


# ─────────────────────────────────────────────
# FATOR SAZONAL
# ─────────────────────────────────────────────
def fator_sazonal(mes: int, tipo: str) -> float:
    if tipo == "cinema":
        fatores_cinema = {
            1: 1.20,
            2: 0.95,
            3: 0.85,
            4: 0.90,
            5: 0.88,
            6: 0.95,
            7: 1.18,
            8: 0.87,
            9: 0.85,
            10: 0.90,
            11: 1.05,
            12: 1.15,
        }
        return fatores_cinema.get(mes, 1.0)

    fatores_clima = {
        1: 1.15, 2: 1.12, 3: 1.08, 4: 1.00,
        5: 0.95, 6: 0.90, 7: 0.88, 8: 0.91,
        9: 0.97, 10: 1.02, 11: 1.08, 12: 1.14,
    }
    return fatores_clima.get(mes, 1.0)


# ─────────────────────────────────────────────
# TEMPERATURA COM SUAVIZAÇÃO
# ─────────────────────────────────────────────
FAIXAS_TEMPERATURA = {
    (0, 5):   (20, 24),
    (6, 11):  (24, 29),
    (12, 16): (29, 35),
    (17, 23): (23, 28),
}

def temperatura_alvo(hora: int) -> float:
    for (h_ini, h_fim), (low, high) in FAIXAS_TEMPERATURA.items():
        if h_ini <= hora <= h_fim:
            return random.uniform(low, high)
    return random.uniform(22, 27)

def simular_temperatura(hora: int, temp_anterior=None) -> float:
    nova = temperatura_alvo(hora)
    if temp_anterior is not None:
        nova = temp_anterior * 0.65 + nova * 0.35
    return round(nova, 2)


# ─────────────────────────────────────────────
# ANOMALIAS MAIS REALISTAS
# ─────────────────────────────────────────────
def aplicar_anomalia(consumo: float, perfil: dict, hora: int, tipo: str):
    anomalia = 0
    tipo_anomalia = "normal"

    prob = random.random()

    if prob < 0.010:
        consumo *= random.uniform(1.6, 2.4)
        anomalia = 1
        tipo_anomalia = "pico"

    elif prob < 0.016:
        consumo *= random.uniform(0.15, 0.45)
        anomalia = 1
        tipo_anomalia = "queda"

    elif prob < 0.019:
        consumo = 0
        anomalia = 1
        tipo_anomalia = "zero"

    elif prob < 0.022:
        consumo = perfil["potencia"] * random.uniform(0.95, 1.10)
        anomalia = 1
        tipo_anomalia = "sobrecarga"

    return consumo, anomalia, tipo_anomalia


# ─────────────────────────────────────────────
# GERAÇÃO DOS REGISTROS
# ─────────────────────────────────────────────
def gerar_registros(df_base: pd.DataFrame) -> list[dict]:
    registros = []

    for _, row in df_base.iterrows():
        nome = str(row["Name"]).strip()
        potencia = float(row["kW AC"])
        tipo = classificar_tipo(nome)
        address = row["Address"]

        perfil = gerar_perfil_local(nome, tipo, potencia)
        consumo_anterior = None

        for d in range(DIAS):
            data_atual = DATA_INICIO + timedelta(days=d)
            dia_semana = data_atual.weekday()
            mes = data_atual.month
            feriado = eh_feriado(data_atual)

            f_sazonal = fator_sazonal(mes, tipo)
            f_dia = fator_dia_semana(dia_semana, tipo)
            f_fer = fator_feriado(tipo, feriado)

            temp_anterior = None

            for hora in range(24):
                data_hora = data_atual + timedelta(hours=hora)
                temperatura = simular_temperatura(hora, temp_anterior)
                temp_anterior = temperatura

                f_hora = fator_horario(hora, tipo, perfil)
                f_temp = 1 + max(0, temperatura - 25) * perfil["sens_temp"]
                ruido = random.uniform(0.94, 1.06)

                consumo_base = potencia * perfil["consumo_base_pct"]

                consumo_operacional = (
                    potencia
                    * f_hora
                    * f_dia
                    * f_sazonal
                    * f_fer
                    * perfil["intensidade"]
                    * f_temp
                    * ruido
                )

                consumo = consumo_base + consumo_operacional

                # autocorrelação temporal
                if consumo_anterior is not None:
                    consumo = consumo * 0.72 + consumo_anterior * 0.28

                consumo, anomalia, tipo_anomalia = aplicar_anomalia(
                    consumo=consumo,
                    perfil=perfil,
                    hora=hora,
                    tipo=tipo,
                )

                consumo = max(0, round(consumo, 2))
                consumo_anterior = consumo

                registros.append({
                    "nome": nome,
                    "tipo_local": tipo,
                    "address": address,
                    "data_hora": data_hora.strftime("%Y-%m-%d %H:%M:%S"),
                    "ano": data_hora.year,
                    "mes": mes,
                    "dia": data_atual.day,
                    "hora": hora,
                    "dia_semana": dia_semana,
                    "fim_de_semana": 1 if dia_semana >= 5 else 0,
                    "feriado": feriado,
                    "temperatura": temperatura,
                    "consumo_kwh": consumo,
                    "anomalia": anomalia,
                    "tipo_anomalia": tipo_anomalia,
                    "potencia_kw_ac_ref": potencia,
                    "consumo_base_estimado": round(consumo_base, 2),
                    "intensidade_operacional_local": perfil["intensidade"],
                    "sensibilidade_temperatura_local": perfil["sens_temp"],
                })

    return registros


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main():
    print(f"Lendo {ARQUIVO_ENTRADA}...")
    df_base = pd.read_csv(ARQUIVO_ENTRADA)

    tipos_encontrados = df_base["Name"].apply(classificar_tipo).unique().tolist()

    if "cinema" not in tipos_encontrados:
        print(
            "\n⚠️ Nenhum cinema encontrado no CSV."
            "\nAdicione linhas com 'cinema', 'theater' ou 'theatre' no campo Name."
            "\nExemplo:"
            "\nName,kW AC,Address"
            "\nCine Lumière,120,Rua das Flores 100\n"
        )

    print(f"Simulando {DIAS} dias para {len(df_base)} instalações...")
    print(f"Tipos detectados: {tipos_encontrados}\n")

    registros = gerar_registros(df_base)

    df_final = pd.DataFrame(registros)
    df_final.to_csv(ARQUIVO_SAIDA, index=False)

    total = len(df_final)
    anomalias = int(df_final["anomalia"].sum())

    print("── Resumo ──────────────────────────────────────")
    print(f"  Registros gerados : {total:,}")
    print(f"  Anomalias         : {anomalias:,} ({anomalias/total*100:.2f}%)")
    print(f"  Período           : {df_final['data_hora'].min()} → {df_final['data_hora'].max()}")
    print(f"  Tipos de local    : {df_final['tipo_local'].unique().tolist()}")

    print("\n  consumo_kwh por tipo")
    print(df_final.groupby("tipo_local")["consumo_kwh"].describe().round(2).to_string())

    print("\n  anomalias por tipo")
    print(df_final.groupby("tipo_local")["anomalia"].sum().to_string())

    print(f"\nArquivo salvo em: {ARQUIVO_SAIDA}")


if __name__ == "__main__":
    main()