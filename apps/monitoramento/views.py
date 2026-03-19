import os
import pandas as pd
from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from django.db import transaction
from django.conf import settings
import traceback

from .models import ConsumoEnergia
from .serializers import ConsumoSerializer
from .services.treinamento import treinar_modelo
from .services.previsao import prever_consumo
from .services.deteccao_anomalia import detectar_anomalias
from .services.modelo_info import obter_info_modelo



# ─────────────────────────────────────────────
# DATASET
# ─────────────────────────────────────────────

import io
import base64
import pandas as pd

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .services.previsao import prever_dataframe
from .services.deteccao_anomalia import detectar_anomalias_dataframe


@api_view(["POST"])
def analisar_csv_api(request):
    arquivo = request.FILES.get("arquivo")

    if not arquivo:
        return Response(
            {"erro": "Nenhum arquivo enviado."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        df = pd.read_csv(arquivo)

        colunas_obrigatorias = [
            "hora",
            "dia_semana",
            "temperatura",
            "mes",
            "fim_de_semana",
            "feriado",
            "potencia_kw_ac_ref",
        ]

        faltando = [c for c in colunas_obrigatorias if c not in df.columns]
        if faltando:
            return Response(
                {"erro": f"Colunas ausentes no CSV: {faltando}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        df = df[df["potencia_kw_ac_ref"] > 0].copy()
        df = df.dropna(subset=colunas_obrigatorias)

        if df.empty:
            return Response(
                {"erro": "Nenhum registro válido encontrado no CSV."},
                status=status.HTTP_400_BAD_REQUEST
            )

        df_resultado = prever_dataframe(df)
        df_resultado = detectar_anomalias_dataframe(df_resultado)

        total = len(df_resultado)
        total_anomalias = int(df_resultado["anomalia_csv"].sum())

        resumo = {
            "total_linhas": total,
            "anomalias_detectadas": total_anomalias,
            "percentual_anomalias": round((total_anomalias / total) * 100, 2) if total > 0 else 0,
            "consumo_previsto_medio_kwh": round(df_resultado["consumo_kwh_previsto"].mean(), 4),
            "consumo_previsto_total_kwh": round(df_resultado["consumo_kwh_previsto"].sum(), 4),
            "fator_utilizacao_medio": round(df_resultado["fator_utilizacao_previsto"].mean(), 4),
        }

        colunas_retorno = [
            "hora",
            "dia_semana",
            "mes",
            "temperatura",
            "fim_de_semana",
            "feriado",
            "potencia_kw_ac_ref",
            "consumo_kwh_previsto",
            "fator_utilizacao_previsto",
            "anomalia_csv",
        ]
        colunas_retorno = [c for c in colunas_retorno if c in df_resultado.columns]

        preview = df_resultado[colunas_retorno].head(100).to_dict(orient="records")

        anomalias = (
            df_resultado[df_resultado["anomalia_csv"] == True][colunas_retorno]
            .to_dict(orient="records")
        )

        graficos = {
            "consumo_por_hora": (
                df_resultado.groupby("hora")["consumo_kwh_previsto"]
                .mean()
                .reset_index()
                .to_dict(orient="records")
            ),
            "consumo_por_mes": (
                df_resultado.groupby("mes")["consumo_kwh_previsto"]
                .mean()
                .reset_index()
                .to_dict(orient="records")
            ),
            "anomalias_por_dia_semana": (
                df_resultado[df_resultado["anomalia_csv"] == True]
                .groupby("dia_semana")
                .size()
                .reset_index(name="total")
                .to_dict(orient="records")
            ),
        }

        buffer = io.StringIO()
        df_resultado[colunas_retorno].to_csv(buffer, index=False)
        csv_base64 = base64.b64encode(buffer.getvalue().encode("utf-8")).decode("utf-8")

        return Response(
            {
                "mensagem": "Arquivo analisado com sucesso.",
                "resumo": resumo,
                "preview": preview,
                "anomalias": anomalias,
                "graficos": graficos,
                "csv_resultado_base64": csv_base64,
            },
            status=status.HTTP_200_OK
        )

    except FileNotFoundError as e:
        return Response(
            {"erro": str(e), "dica": "Treine o modelo primeiro via POST /api/treinar/"},
            status=status.HTTP_400_BAD_REQUEST
        )
    except Exception as e:
        return Response(
            {"erro": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

def to_bool(value):
    if pd.isna(value):
        return False
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return bool(value)
    return str(value).strip().lower() in ["1", "true", "sim", "yes"]


@api_view(["POST"])
def upload_dataset_api(request):
    arquivo = request.FILES.get("arquivo")

    if not arquivo:
        return Response(
            {"erro": "Nenhum arquivo enviado."},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        total_importado = 0
        chunk_size = 20000
        batch_size = 5000

        for chunk in pd.read_csv(arquivo, chunksize=chunk_size):
            print(f"[DEBUG] Chunk recebido com {len(chunk)} linhas")

            # limpeza básica
            chunk = chunk.where(pd.notna(chunk), None)

            # conversões vetorizadas
            chunk["data_hora"] = pd.to_datetime(chunk["data_hora"], errors="coerce")

            colunas_int = ["ano", "mes", "dia", "hora", "dia_semana"]
            for col in colunas_int:
                chunk[col] = pd.to_numeric(chunk[col], errors="coerce")

            colunas_float = [
                "temperatura",
                "consumo_kwh",
                "potencia_kw_ac_ref",
                "consumo_base_estimado",
                "intensidade_operacional_local",
                "sensibilidade_temperatura_local",
            ]
            for col in colunas_float:
                if col in chunk.columns:
                    chunk[col] = pd.to_numeric(chunk[col], errors="coerce")

            # remove linhas inválidas
            antes = len(chunk)
            chunk = chunk.dropna(subset=[
                "nome",
                "tipo_local",
                "data_hora",
                "ano",
                "mes",
                "dia",
                "hora",
                "dia_semana",
                "consumo_kwh",
                "potencia_kw_ac_ref",
            ])
            print(f"[DEBUG] Chunk após limpeza: {len(chunk)} linhas (removeu {antes - len(chunk)})")

            registros = []

            for row in chunk.itertuples(index=False):
                data_hora_aware = timezone.make_aware(
                    row.data_hora.to_pydatetime(),
                    timezone.get_current_timezone()
                )

                registros.append(
                    ConsumoEnergia(
                        nome=str(row.nome).strip(),
                        tipo_local=str(row.tipo_local).strip(),
                        address=str(row.address).strip() if getattr(row, "address", None) else None,

                        data_hora=data_hora_aware,

                        ano=int(row.ano),
                        mes=int(row.mes),
                        dia=int(row.dia),
                        hora=int(row.hora),
                        dia_semana=int(row.dia_semana),

                        fim_de_semana=to_bool(getattr(row, "fim_de_semana", False)),
                        feriado=to_bool(getattr(row, "feriado", False)),

                        temperatura=float(row.temperatura) if row.temperatura is not None else None,
                        consumo_kwh=float(row.consumo_kwh),

                        anomalia=to_bool(getattr(row, "anomalia", False)),
                        tipo_anomalia=str(getattr(row, "tipo_anomalia", "normal")).strip(),

                        potencia_kw_ac_ref=float(row.potencia_kw_ac_ref),

                        consumo_base_estimado=float(row.consumo_base_estimado) if getattr(row, "consumo_base_estimado", None) is not None else None,
                        intensidade_operacional_local=float(row.intensidade_operacional_local) if getattr(row, "intensidade_operacional_local", None) is not None else None,
                        sensibilidade_temperatura_local=float(row.sensibilidade_temperatura_local) if getattr(row, "sensibilidade_temperatura_local", None) is not None else None,
                    )
                )

            with transaction.atomic():
                ConsumoEnergia.objects.bulk_create(registros, batch_size=batch_size)

            total_importado += len(registros)
            print(f"[DEBUG] Total de objetos importados até agora: {total_importado}")

        return Response(
            {
                "mensagem": "CSV importado com sucesso.",
                "total_importado": total_importado
            },
            status=status.HTTP_201_CREATED
        )

    except Exception as e:
        return Response(
            {"erro": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )

# ─────────────────────────────────────────────
# CONSUMO
# ─────────────────────────────────────────────

@api_view(["GET"])
def listar_consumo(request):
    limite = int(request.GET.get("limite", 1000))
    dados = ConsumoEnergia.objects.all().order_by("-data_hora")[:limite]
    serializer = ConsumoSerializer(dados, many=True)
    return Response(serializer.data)

# ─────────────────────────────────────────────
# MODELO
# ─────────────────────────────────────────────

@api_view(["POST"])
def treinar_modelo_api(request):
    try:
        resultado = treinar_modelo()
        return Response(resultado, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"erro": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["POST"])
def prever_consumo_api(request):
    try:
        resultado = prever_consumo(
            hora=int(request.data.get("hora")),
            dia_semana=int(request.data.get("dia_semana")),
            temperatura=float(request.data.get("temperatura")),
            mes=int(request.data.get("mes")),
            potencia_kw_ac_ref=float(request.data.get("potencia_kw_ac_ref")),
            fim_de_semana=to_bool(request.data.get("fim_de_semana")),
            feriado=to_bool(request.data.get("feriado")),
            consumo_base_estimado=(
                float(request.data.get("consumo_base_estimado"))
                if request.data.get("consumo_base_estimado") not in [None, ""]
                else None
            ),
            intensidade_operacional_local=float(
                request.data.get("intensidade_operacional_local", 1.0)
            ),
            sensibilidade_temperatura_local=float(
                request.data.get("sensibilidade_temperatura_local", 0.015)
            ),
        )
        return Response(resultado, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"[ERRO /api/prever/] {e}")
        return Response({"erro": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def info_modelo_api(request):
    try:
        info = obter_info_modelo()
        return Response(info, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({"erro": str(e)}, status=status.HTTP_400_BAD_REQUEST)


# ─────────────────────────────────────────────
# ANOMALIAS
# ─────────────────────────────────────────────

@api_view(["POST"])
def detectar_anomalias_api(request):
    try:
        resultado = detectar_anomalias()

        limite = int(request.data.get("limite", 1000))
        dados = ConsumoEnergia.objects.filter(anomalia=True).order_by("-data_hora")[:limite]
        serializer = ConsumoSerializer(dados, many=True)

        return Response(
            {
                **resultado,
                "anomalias": serializer.data
            },
            status=status.HTTP_200_OK
        )
    except Exception as e:
        print(f"[ERRO /api/detectar-anomalias/] {repr(e)}")
        return Response({"erro": str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(["GET"])
def listar_anomalias(request):
    limite = int(request.GET.get("limite", 1000))
    dados = ConsumoEnergia.objects.filter(anomalia=True).order_by("-data_hora")[:limite]
    serializer = ConsumoSerializer(dados, many=True)
    return Response(serializer.data)

@api_view(["DELETE"])
def limpar_base_api(request):
    try:
        arquivos_removidos = []

        # Apaga todos os registros da tabela
        with transaction.atomic():
            total = ConsumoEnergia.objects.count()
            ConsumoEnergia.objects.all().delete()

        # Caminhos corretos dos arquivos do modelo
        model_dir = os.path.join(settings.BASE_DIR, "apps", "monitoramento", "ml_models")
        possiveis_arquivos = [
            os.path.join(model_dir, "modelo_consumo.pkl"),
            os.path.join(model_dir, "modelo_consumo_info.json"),
        ]

        # Tenta remover arquivos e mostra debug
        for caminho in possiveis_arquivos:
            try:
                if os.path.exists(caminho):
                    os.remove(caminho)
                    arquivos_removidos.append(os.path.basename(caminho))
                else:
                    print(f"Arquivo não encontrado: {caminho}")
            except Exception as e_file:
                print(f"Erro ao remover arquivo {caminho}: {e_file}")
                traceback.print_exc()

        return Response(
            {
                "mensagem": "Base de dados e arquivos do modelo limpos com sucesso.",
                "registros_removidos": total,
                "arquivos_modelo_removidos": arquivos_removidos,
            },
            status=status.HTTP_200_OK
        )

    except Exception as e:
        traceback.print_exc()
        return Response(
            {"erro": str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )