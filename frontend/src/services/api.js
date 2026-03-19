const API_BASE_URL = "http://127.0.0.1:8000/api";

export async function listarConsumo(limite = 1000) {
  const response = await fetch(`${API_BASE_URL}/consumo/?limite=${limite}`);
  if (!response.ok) throw new Error("Erro ao buscar consumo");
  return response.json();
}

export async function listarAnomalias(limite = 1000) {
  const response = await fetch(`${API_BASE_URL}/anomalias/?limite=${limite}`);
  if (!response.ok) throw new Error("Erro ao buscar anomalias");
  return response.json();
}

export async function treinarModelo() {
  const response = await fetch(`${API_BASE_URL}/modelo/treinar/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!response.ok) throw new Error("Erro ao treinar modelo");
  return response.json();
}

export async function obterInfoModelo() {
  const response = await fetch(`${API_BASE_URL}/modelo-info/`);
  if (!response.ok) throw new Error("Modelo não treinado ainda");
  return response.json();
}

export async function preverConsumo(payload) {
  const response = await fetch(`${API_BASE_URL}/prever/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  if (!response.ok) throw new Error("Erro ao prever consumo");
  return response.json();
}

export async function uploadCSV(file) {
  const formData = new FormData();
  formData.append("arquivo", file);
  const response = await fetch(`${API_BASE_URL}/upload/`, {
    method: "POST",
    body: formData,
  });
  if (!response.ok) throw new Error("Erro ao enviar CSV");
  return response.json();
}

export async function analisarCSV(file) {
  const formData = new FormData();
  formData.append("arquivo", file);

  const response = await fetch(`${API_BASE_URL}/analisar-csv/`, {
    method: "POST",
    body: formData,
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.erro || "Erro ao analisar CSV");
  }

  return data;
}

export async function detectarAnomalias() {
  const response = await fetch(`${API_BASE_URL}/detectar-anomalias/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
  });
  if (!response.ok) throw new Error("Erro ao detectar anomalias");
  return response.json();
}

export async function limparBase() {
  const response = await fetch(`${API_BASE_URL}/limpar-base/`, {
    method: "DELETE",
  });

  const data = await response.json();

  if (!response.ok) {
    throw new Error(data.erro || "Erro ao limpar a base.");
  }

  return data;
}