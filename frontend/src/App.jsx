import { useState, useEffect, useCallback, useRef } from "react";
import {
  listarConsumo,
  listarAnomalias,
  treinarModelo,
  obterInfoModelo,
  preverConsumo,
  uploadCSV,
  analisarCSV,
  detectarAnomalias,
  limparBase,
} from "./services/api";
import "./App.css";

/* ─────────────────────────────────────────
   MICRO COMPONENTS
───────────────────────────────────────── */

function Toast({ toasts }) {
  return (
    <div className="toast-stack">
      {toasts.map((t) => (
        <div key={t.id} className={`toast toast--${t.type}`}>
          <span className="toast-icon">
            {t.type === "ok" ? "✓" : t.type === "err" ? "✕" : "⟳"}
          </span>
          {t.msg}
        </div>
      ))}
    </div>
  );
}

function Stat({ label, value, sub, accent, warn }) {
  return (
    <div className={`stat-card ${accent ? "stat-card--accent" : ""} ${warn ? "stat-card--warn" : ""}`}>
      <span className="stat-value">{value}</span>
      <span className="stat-label">{label}</span>
      {sub && <span className="stat-sub">{sub}</span>}
    </div>
  );
}

function DataTable({ rows, cols, limit = 20 }) {
  if (!rows || rows.length === 0)
    return <p className="empty">Nenhum dado encontrado.</p>;
  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>{cols.map((c) => <th key={c.key}>{c.label}</th>)}</tr>
        </thead>
        <tbody>
          {rows.slice(0, limit).map((row, i) => (
            <tr key={i} className={row.anomalia || row.anomalia_csv ? "row--anomaly" : ""}>
              {cols.map((c) => (
                <td key={c.key}>
                  {c.render ? c.render(row[c.key], row) : String(row[c.key] ?? "—")}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
      {rows.length > limit && (
        <p className="table-more">Mostrando {limit} de {rows.length} registros</p>
      )}
    </div>
  );
}

function Btn({ label, loading, onClick, icon, variant = "default", fullWidth }) {
  return (
    <button
      className={`btn btn--${variant} ${loading ? "btn--loading" : ""} ${fullWidth ? "btn--full" : ""}`}
      onClick={onClick}
      disabled={loading}
    >
      {loading ? <span className="spinner" /> : <span className="btn-icon">{icon}</span>}
      {label}
    </button>
  );
}

function Field({ label, ...props }) {
  return (
    <label className="field">
      <span className="field-label">{label}</span>
      <input className="field-input" {...props} />
    </label>
  );
}

function SectionDivider({ label }) {
  return (
    <div className="section-divider">
      <span className="section-divider-line" />
      <span className="section-divider-label">{label}</span>
      <span className="section-divider-line" />
    </div>
  );
}

/* ─────────────────────────────────────────
   MINI CHARTS (SVG — sem dependências)
───────────────────────────────────────── */

function BarChart({ data, color = "#3b82f6", height = 80 }) {
  if (!data || data.length === 0) return null;
  const max = Math.max(...data.map((d) => d.value), 0.001);
  const w = 100 / data.length;
  return (
    <div className="mini-chart">
      <svg viewBox={`0 0 100 ${height}`} preserveAspectRatio="none" className="mini-chart-svg">
        {data.map((d, i) => {
          const barH = (d.value / max) * (height - 6);
          return (
            <g key={i}>
              <rect
                x={i * w + 0.5}
                y={height - barH}
                width={w - 1}
                height={barH}
                fill={color}
                opacity="0.75"
                rx="1"
              />
            </g>
          );
        })}
      </svg>
      <div className="mini-chart-labels">
        {data.filter((_, i) => i % Math.ceil(data.length / 6) === 0).map((d, i) => (
          <span key={i}>{d.label}</span>
        ))}
      </div>
    </div>
  );
}

function LineChart({ data, color = "#06d6a0", height = 80 }) {
  if (!data || data.length < 2) return null;
  const max = Math.max(...data.map((d) => d.value), 0.001);
  const min = Math.min(...data.map((d) => d.value));
  const range = max - min || 1;
  const W = 200, H = height;
  const pts = data.map((d, i) => {
    const x = (i / (data.length - 1)) * W;
    const y = H - ((d.value - min) / range) * (H - 8) - 4;
    return `${x},${y}`;
  });
  const fillPts = `0,${H} ${pts.join(" ")} ${W},${H}`;
  return (
    <div className="mini-chart">
      <svg viewBox={`0 0 ${W} ${H}`} preserveAspectRatio="none" className="mini-chart-svg">
        <defs>
          <linearGradient id={`lg-${color.replace("#","")}`} x1="0" y1="0" x2="0" y2="1">
            <stop offset="0%" stopColor={color} stopOpacity="0.35" />
            <stop offset="100%" stopColor={color} stopOpacity="0.02" />
          </linearGradient>
        </defs>
        <polygon points={fillPts} fill={`url(#lg-${color.replace("#","")})`} />
        <polyline points={pts.join(" ")} fill="none" stroke={color} strokeWidth="1.5" />
      </svg>
      <div className="mini-chart-labels">
        {data.filter((_, i) => i % Math.ceil(data.length / 6) === 0).map((d, i) => (
          <span key={i}>{d.label}</span>
        ))}
      </div>
    </div>
  );
}

function DonutChart({ pct, color = "#ef4444", size = 80 }) {
  const r = 28, cx = 40, cy = 40;
  const circ = 2 * Math.PI * r;
  const dash = (pct / 100) * circ;
  return (
    <svg viewBox="0 0 80 80" width={size} height={size}>
      <circle cx={cx} cy={cy} r={r} fill="none" stroke="#1e2535" strokeWidth="8" />
      <circle
        cx={cx} cy={cy} r={r}
        fill="none"
        stroke={color}
        strokeWidth="8"
        strokeDasharray={`${dash} ${circ - dash}`}
        strokeLinecap="round"
        transform="rotate(-90 40 40)"
        style={{ transition: "stroke-dasharray 0.6s ease" }}
      />
      <text x={cx} y={cy + 5} textAnchor="middle" fill={color} fontSize="11" fontFamily="'DM Mono',monospace" fontWeight="500">
        {pct.toFixed(1)}%
      </text>
    </svg>
  );
}

/* ─────────────────────────────────────────
   DATA ANALYTICS PAGE
───────────────────────────────────────── */

function DadosPage({ analiseResult, loading, onLoad }) {
  const [filtro, setFiltro] = useState("");

  const resumo = analiseResult?.resumo || {};
  const preview = analiseResult?.preview || [];
  const graficos = analiseResult?.graficos || {};

  const total = resumo.total_linhas ?? 0;
  const anomalas = resumo.anomalias_detectadas ?? 0;
  const pctAnomalia = resumo.percentual_anomalias ?? 0;
  const consumoMedio = resumo.consumo_previsto_medio_kwh ?? 0;
  const consumoTotal = resumo.consumo_previsto_total_kwh ?? 0;

  const consumoMax = preview.length
    ? Math.max(...preview.map((r) => Number(r.consumo_kwh_previsto) || 0))
    : 0;

  const consumoMin = preview.length
    ? Math.min(...preview.map((r) => Number(r.consumo_kwh_previsto) || 0))
    : 0;

  const porHora = Array.from({ length: 24 }, (_, h) => {
    const item = (graficos.consumo_por_hora || []).find((r) => Number(r.hora) === h);
    return {
      label: `${h}h`,
      value: Number(item?.consumo_kwh_previsto) || 0,
    };
  });

  const meses = ["Jan","Fev","Mar","Abr","Mai","Jun","Jul","Ago","Set","Out","Nov","Dez"];
  const porMes = meses.map((m, i) => {
    const item = (graficos.consumo_por_mes || []).find((r) => Number(r.mes) === i + 1);
    return {
      label: m,
      value: Number(item?.consumo_kwh_previsto) || 0,
    };
  });

  const diasLabel = ["Seg","Ter","Qua","Qui","Sex","Sáb","Dom"];
  const anomaliasPorDia = diasLabel.map((d, i) => {
    const item = (graficos.anomalias_por_dia_semana || []).find(
      (r) => Number(r.dia_semana) === i
    );
    return {
      label: d,
      value: Number(item?.total) || 0,
    };
  });

  const filtered = filtro
    ? preview.filter(
        (r) =>
          String(r.hora ?? "").toLowerCase().includes(filtro.toLowerCase()) ||
          String(r.mes ?? "").toLowerCase().includes(filtro.toLowerCase())
      )
    : preview;

  return (
    <section className="page">
      <h2 className="page-title">📋 Análise de Dados</h2>
      <p className="page-sub">
        Visão geral do CSV analisado: consumo previsto, anomalias, distribuições e preview.
      </p>

      <div className="step-card" style={{ marginBottom: 20 }}>
        <div className="step-actions">
          <Btn
            label="Analisar CSV"
            loading={loading}
            onClick={onLoad}
            icon="↻"
            variant="primary"
          />
        </div>
      </div>

      {!analiseResult && !loading && (
        <p className="empty" style={{ marginTop: 40 }}>
          Faça a análise de um CSV para visualizar os dados.
        </p>
      )}

      {analiseResult && (
        <>
          <div className="stats-row" style={{ marginBottom: 20 }}>
            <Stat label="Total Registros" value={total.toLocaleString()} sub="no CSV" accent />
            <Stat label="Anomalias" value={anomalas.toLocaleString()} sub={`${pctAnomalia.toFixed(1)}% do total`} warn />
            <Stat label="Consumo Médio" value={`${Number(consumoMedio).toFixed(2)} kWh`} sub="média prevista" />
            <Stat label="Consumo Total" value={`${Number(consumoTotal).toFixed(2)} kWh`} sub="soma prevista" />
            <Stat label="Pico de Consumo" value={`${Number(consumoMax).toFixed(2)} kWh`} sub="maior do preview" />
          </div>

          <div className="charts-grid">
            <div className="chart-card">
              <div className="chart-card-header">
                <span className="chart-card-title">Consumo Médio por Hora</span>
                <span className="chart-card-tag chart-card-tag--blue">kWh</span>
              </div>
              <BarChart data={porHora} color="#3b82f6" height={90} />
            </div>

            <div className="chart-card">
              <div className="chart-card-header">
                <span className="chart-card-title">Consumo Médio por Mês</span>
                <span className="chart-card-tag chart-card-tag--green">kWh</span>
              </div>
              <LineChart data={porMes} color="#06d6a0" height={90} />
            </div>

            <div className="chart-card">
              <div className="chart-card-header">
                <span className="chart-card-title">Anomalias por Dia da Semana</span>
                <span className="chart-card-tag chart-card-tag--red">count</span>
              </div>
              <BarChart data={anomaliasPorDia} color="#ef4444" height={90} />
            </div>

            <div className="chart-card chart-card--split">
              <div className="chart-half">
                <span className="chart-card-title">Taxa de Anomalia</span>
                <div style={{ display: "flex", justifyContent: "center", marginTop: 8 }}>
                  <DonutChart pct={pctAnomalia} color="#ef4444" size={90} />
                </div>
              </div>
              <div className="chart-half">
                <span className="chart-card-title">Resumo</span>
                <div className="tipo-list">
                  <div className="tipo-row">
                    <span className="tipo-name">Linhas analisadas</span>
                    <span className="tipo-cnt">{total}</span>
                  </div>
                  <div className="tipo-row">
                    <span className="tipo-name">Anomalias</span>
                    <span className="tipo-cnt">{anomalas}</span>
                  </div>
                  <div className="tipo-row">
                    <span className="tipo-name">Consumo médio</span>
                    <span className="tipo-cnt">{Number(consumoMedio).toFixed(2)}</span>
                  </div>
                  <div className="tipo-row">
                    <span className="tipo-name">Consumo total</span>
                    <span className="tipo-cnt">{Number(consumoTotal).toFixed(2)}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div className="card">
            <div className="table-toolbar">
              <h3 className="card-title" style={{ marginBottom: 0 }}>
                Preview — {filtered.length.toLocaleString()} exibidos
              </h3>
              <input
                className="search-input"
                placeholder="🔎 Filtrar por hora ou mês..."
                value={filtro}
                onChange={(e) => setFiltro(e.target.value)}
              />
            </div>

            <DataTable
              rows={filtered}
              limit={100}
              cols={[
                { key: "hora", label: "Hora" },
                { key: "dia_semana", label: "Dia semana" },
                { key: "mes", label: "Mês" },
                { key: "temperatura", label: "Temp °C" },
                { key: "potencia_kw_ac_ref", label: "Potência kW" },
                {
                  key: "consumo_kwh_previsto",
                  label: "Previsto kWh",
                  render: (v) => Number(v ?? 0).toFixed(3),
                },
                {
                  key: "fator_utilizacao_previsto",
                  label: "Fator Util.",
                  render: (v) => Number(v ?? 0).toFixed(4),
                },
                {
                  key: "anomalia_csv",
                  label: "Status",
                  render: (v) =>
                    v ? (
                      <span className="badge-anomaly">⚠ ANOMALIA</span>
                    ) : (
                      <span className="badge-ok">✓ Normal</span>
                    ),
                },
              ]}
            />
          </div>
        </>
      )}
    </section>
  );
}

/* ─────────────────────────────────────────
   APP
───────────────────────────────────────── */
export default function App() {
  const [active, setActive]           = useState("preparar");
  const [toasts, setToasts]           = useState([]);
  const [loading, setLoading]         = useState({});
  const [consumo, setConsumo]         = useState([]);
  const [anomalias, setAnomalias]     = useState([]);
  const [modeloInfo, setModeloInfo]   = useState(null);
  const [previsao, setPrevisao]       = useState(null);
  const [analiseResult, setAnaliseResult] = useState(null);
  const [uploadResult, setUploadResult]   = useState(null);

  const [form, setForm] = useState({
    hora: 14, dia_semana: 2, temperatura: 30,
    potencia_kw_ac_ref: 30, mes: 6,
    fim_de_semana: false, feriado: false,
    consumo_base_estimado: "",
    intensidade_operacional_local: 1.0,
    sensibilidade_temperatura_local: 0.015,
  });
  const [arquivoUpload, setArquivoUpload] = useState(null);
  const [arquivoAnalise, setArquivoAnalise] = useState(null);

  /* ── toasts ── */
  const toast = useCallback((msg, type = "ok") => {
    const id = Date.now();
    setToasts((p) => [...p, { id, msg, type }]);
    setTimeout(() => setToasts((p) => p.filter((t) => t.id !== id)), 4500);
  }, []);

  const load = (key, fn) => async () => {
    setLoading((p) => ({ ...p, [key]: true }));
    try { await fn(); }
    catch (e) { toast(e.message || "Erro inesperado.", "err"); }
    finally { setLoading((p) => ({ ...p, [key]: false })); }
  };

  useEffect(() => {
    obterInfoModelo().then(setModeloInfo).catch(() => {});
  }, []);

  /* ── handlers ── */
  const handleUpload = load("upload", async () => {
    if (!arquivoUpload) { toast("Selecione um arquivo CSV.", "err"); return; }
    const res = await uploadCSV(arquivoUpload);
    setUploadResult(res);
    toast(`${res.mensagem} — ${res.total_importado?.toLocaleString()} registros importados.`);
  });

  const handleTreinar = load("treinar", async () => {
    toast("Treinando modelo, aguarde...", "info");
    const res = await treinarModelo();
    const info = await obterInfoModelo();
    setModeloInfo(info);
    toast(`Modelo treinado! R²: ${res.metricas?.r2?.toFixed(4)} | MAE: ${res.metricas?.mae?.toFixed(4)}`);
  });

  const handleLimparBase = load("limparBase", async () => {
    const confirmar = window.confirm(
      "Tem certeza que deseja apagar todos os dados importados e limpar o modelo treinado?"
    );

    if (!confirmar) return;

    const res = await limparBase();

    setConsumo([]);
    setAnomalias([]);
    setModeloInfo(null);
    setPrevisao(null);
    setAnaliseResult(null);
    setUploadResult(null);
    setArquivoUpload(null);
    setArquivoAnalise(null);
    ultimaAnaliseRef.current = null;

    toast(
      `${res.mensagem} ${res.registros_removidos?.toLocaleString()} registros removidos.`,
      "ok"
    );
  });

  const handlePrever = load("prever", async () => {
    const payload = {
      ...form,
      fim_de_semana: form.fim_de_semana ? 1 : 0,
      feriado: form.feriado ? 1 : 0,
      consumo_base_estimado: form.consumo_base_estimado === "" ? null : Number(form.consumo_base_estimado),
    };
    const res = await preverConsumo(payload);
    setPrevisao(res);
    toast("Previsão calculada com sucesso.");
  });

  /* ── baixar CSV das anomalias ── */
  const handleBaixarAnomalias = load("anomalias", async () => {
    if (!analiseResult) {
      toast("Analise um CSV primeiro para exportar as anomalias.", "err");
      return;
    }

    const dadosAnomalia = analiseResult?.anomalias || [];

    if (!dadosAnomalia.length) {
      toast("Nenhuma anomalia encontrada no CSV analisado.", "err");
      return;
    }

    const cols = [
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
    ];

    const header = cols.join(",");
    const rows = dadosAnomalia.map((r) =>
      cols.map((c) => JSON.stringify(r[c] ?? "")).join(",")
    );
    const csv = [header, ...rows].join("\n");

    const blob = new Blob([csv], { type: "text/csv;charset=utf-8;" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = "anomalias_csv_analisado.csv";
    a.click();
    URL.revokeObjectURL(url);

    toast(`${dadosAnomalia.length} anomalias exportadas para CSV.`);
  });

  const handleListarConsumo = load("consumo", async () => {
    const res = await listarConsumo(2000);
    setConsumo(res);
    toast(`${res.length} registros carregados.`);
  });

  const ultimaAnaliseRef = useRef(null);

  const handleAnalisar = load("analisar", async () => {
    if (!arquivoAnalise) {
      toast("Selecione um arquivo CSV.", "err");
      return;
    }

    const chaveArquivo = `${arquivoAnalise.name}-${arquivoAnalise.size}-${arquivoAnalise.lastModified}`;

    if (analiseResult && ultimaAnaliseRef.current === chaveArquivo) {
      toast("Usando análise já carregada para este arquivo.", "info");
      return;
    }

    toast("Aplicando modelo + IsolationForest no CSV...", "info");

    const res = await analisarCSV(arquivoAnalise);

    console.log("RESPOSTA ANALISE:", res);
    console.log("PREVIEW:", res.preview);
    console.log("ANOMALIAS:", res.anomalias);
    console.log("RESUMO:", res.resumo);

    setAnaliseResult(res);
    ultimaAnaliseRef.current = chaveArquivo;

    toast(`Análise concluída! ${res.resumo?.anomalias_detectadas} anomalias detectadas.`);
  });

  const handleDownloadCSV = () => {
    if (!analiseResult?.csv_resultado_base64) return;
    const blob = new Blob([atob(analiseResult.csv_resultado_base64)], { type: "text/csv" });
    const url  = URL.createObjectURL(blob);
    const a    = document.createElement("a");
    a.href = url; a.download = "resultado_analise.csv"; a.click();
    URL.revokeObjectURL(url);
  };

  const f = (key) => (e) =>
    setForm((p) => ({ ...p, [key]: e.target.type === "checkbox" ? e.target.checked : e.target.value }));

  const isLoading = (key) => !!loading[key];

  const navItems = [
    { id: "preparar", icon: "⚙",  label: "Preparar & Treinar" },
    { id: "prever",   icon: "📈", label: "Previsão" },
    { id: "analisar", icon: "🔍", label: "Analisar CSV" },
    { id: "detectar", icon: "⚠",  label: "Anomalias" },
    { id: "consumo",  icon: "📊", label: "Dados" },
  ];

  return (
    <>
      <Toast toasts={toasts} />

      {/* ── SIDEBAR ── */}
      <aside className="sidebar">
        <div className="logo">
          <span className="logo-bolt">⚡</span>
          <div className="logo-text">Power<strong>Predict</strong></div>
        </div>

        <nav className="nav">
          {navItems.map((item) => (
            <button
              key={item.id}
              className={`nav-item ${active === item.id ? "nav-item--active" : ""}`}
              onClick={() => setActive(item.id)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}
        </nav>

        {modeloInfo ? (
          <div className="sidebar-model-badge sidebar-model-badge--active">
            <span className="badge-dot" />
            <div className="badge-info">
              <span className="badge-title">Modelo ativo</span>
              <span className="badge-r2">R² {modeloInfo.metricas?.r2?.toFixed(4)}</span>
            </div>
          </div>
        ) : (
          <div className="sidebar-model-badge sidebar-model-badge--none">
            <span className="badge-dot badge-dot--off" />
            <div className="badge-info">
              <span className="badge-title">Sem modelo</span>
              <span className="badge-r2">Treine primeiro</span>
            </div>
          </div>
        )}
      </aside>

      {/* ── MAIN ── */}
      <main className="main">

        {/* ══ PREPARAR & TREINAR ══ */}
        {active === "preparar" && (
          <section className="page">
            <h2 className="page-title">⚙ Preparar & Treinar</h2>
            <p className="page-sub">Importe o dataset histórico e, em seguida, treine o modelo de previsão de consumo.</p>

            <div className="step-card">
              <div className="step-header">
                <span className="step-num">1</span>
                <div>
                  <h3 className="step-title">Upload do Dataset</h3>
                  <p className="step-desc">Envie o CSV histórico para popular o banco de dados.</p>
                </div>
              </div>
              <div
                className={`dropzone ${arquivoUpload ? "dropzone--selected" : ""}`}
                onClick={() => document.getElementById("f-upload").click()}
              >
                <span className="dropzone-icon">{arquivoUpload ? "✅" : "📂"}</span>
                <span className="dropzone-label">{arquivoUpload ? arquivoUpload.name : "Clique para selecionar um arquivo CSV"}</span>
                {arquivoUpload && <span className="dropzone-size">{(arquivoUpload.size / 1024).toFixed(1)} KB</span>}
                <input id="f-upload" type="file" accept=".csv" style={{ display: "none" }}
                  onChange={(e) => { setArquivoUpload(e.target.files[0]); setUploadResult(null); }} />
              </div>
              <div className="step-actions">
                <Btn
                  label="Importar Dataset"
                  loading={isLoading("upload")}
                  onClick={handleUpload}
                  icon="⬆"
                  variant="primary"
                />

                <Btn
                  label="Limpar Base"
                  loading={isLoading("limparBase")}
                  onClick={handleLimparBase}
                  icon="🗑"
                  variant="danger"
                />

                {arquivoUpload && !isLoading("upload") && (
                  <button
                    className="btn-link"
                    onClick={() => {
                      setArquivoUpload(null);
                      setUploadResult(null);
                    }}
                  >
                    Remover arquivo
                  </button>
                )}
              </div>
              {uploadResult && (
                <div className="result-inline result-inline--ok">
                  <span>✓</span>
                  <span><strong>{uploadResult.total_importado?.toLocaleString()}</strong> registros importados com sucesso.</span>
                </div>
              )}
              <div className="info-box" style={{ marginTop: 16 }}>
                <strong>Colunas esperadas:</strong>
                <code>nome, tipo_local, data_hora, ano, mes, dia, hora, dia_semana, fim_de_semana, feriado, temperatura, consumo_kwh, potencia_kw_ac_ref, consumo_base_estimado, intensidade_operacional_local, sensibilidade_temperatura_local</code>
              </div>
            </div>

            <SectionDivider label="após importar o dataset" />

            <div className="step-card">
              <div className="step-header">
                <span className="step-num">2</span>
                <div>
                  <h3 className="step-title">Treinamento do Modelo</h3>
                  <p className="step-desc">Treina um RandomForestRegressor usando os registros sem anomalia. O modelo aprende a prever o <em>fator de utilização</em>.</p>
                </div>
              </div>
              <div className="step-actions">
                <Btn label="Treinar Modelo" loading={isLoading("treinar")} onClick={handleTreinar} icon="🚀" variant="primary" />
                <Btn label="Atualizar métricas" loading={false}
                  onClick={() => obterInfoModelo().then(setModeloInfo).then(() => toast("Métricas atualizadas.")).catch(() => toast("Modelo não encontrado.", "err"))}
                  icon="↻" variant="ghost" />
              </div>
              {modeloInfo && (
                <>
                  <div className="stats-row" style={{ marginTop: 20 }}>
                    <Stat label="R²"        value={modeloInfo.metricas?.r2?.toFixed(4)}   sub="Coef. determinação" accent />
                    <Stat label="MAE"       value={modeloInfo.metricas?.mae?.toFixed(4)}  sub="Erro absoluto médio" />
                    <Stat label="RMSE"      value={modeloInfo.metricas?.rmse?.toFixed(4)} sub="Raiz erro quadrático" />
                    <Stat label="Registros" value={modeloInfo.total_registros?.toLocaleString()} sub="Usados no treino" />
                  </div>
                  <div className="card" style={{ marginTop: 16 }}>
                    <h3 className="card-title">Importância das Features</h3>
                    {Object.entries(modeloInfo.importancia_das_features || {})
                      .sort(([, a], [, b]) => b - a)
                      .map(([feat, val]) => (
                        <div key={feat} className="feat-bar">
                          <span className="feat-name">{feat}</span>
                          <div className="feat-track">
                            <div className="feat-fill" style={{ width: `${(val * 100).toFixed(1)}%` }} />
                          </div>
                          <span className="feat-pct">{(val * 100).toFixed(1)}%</span>
                        </div>
                      ))}
                  </div>
                  <div className="info-box" style={{ marginTop: 12 }}>
                    <strong>Treinado em:</strong> {new Date(modeloInfo.data_treinamento).toLocaleString("pt-BR")}
                    &nbsp;·&nbsp; <strong>Target:</strong> {modeloInfo.target}
                  </div>
                </>
              )}
            </div>
          </section>
        )}

        {/* ══ PREVISÃO ══ */}
        {active === "prever" && (
          <section className="page">
            <h2 className="page-title">📈 Previsão de Consumo</h2>
            <p className="page-sub">Prevê o consumo (kWh) para um único instante usando o modelo treinado.</p>
            <div className="form-grid card">
              <Field label="Hora (0-23)"              type="number" value={form.hora}                          onChange={f("hora")}                          min={0}  max={23} />
              <Field label="Dia da semana (0=seg)"    type="number" value={form.dia_semana}                    onChange={f("dia_semana")}                    min={0}  max={6} />
              <Field label="Mês (1-12)"               type="number" value={form.mes}                           onChange={f("mes")}                           min={1}  max={12} />
              <Field label="Temperatura (°C)"         type="number" value={form.temperatura}                   onChange={f("temperatura")}                   step="0.1" />
              <Field label="Potência instalada (kW)"  type="number" value={form.potencia_kw_ac_ref}            onChange={f("potencia_kw_ac_ref")}            step="0.01" />
              <Field label="Consumo base (kWh)"       type="number" value={form.consumo_base_estimado}         onChange={f("consumo_base_estimado")}         step="0.01" placeholder="Opcional" />
              <Field label="Intensidade operacional"  type="number" value={form.intensidade_operacional_local} onChange={f("intensidade_operacional_local")} step="0.01" />
              <Field label="Sensib. temperatura"      type="number" value={form.sensibilidade_temperatura_local} onChange={f("sensibilidade_temperatura_local")} step="0.001" />
              <div className="field-check">
                <label><input type="checkbox" checked={form.fim_de_semana} onChange={f("fim_de_semana")} /> Fim de semana</label>
                <label><input type="checkbox" checked={form.feriado} onChange={f("feriado")} /> Feriado</label>
              </div>
            </div>
            <Btn label="Calcular Previsão" loading={isLoading("prever")} onClick={handlePrever} icon="⚡" variant="primary" />
            {previsao && (
              <div className="result-card">
                <div className="result-main">
                  <span className="result-value">{previsao.previsao_consumo_kwh?.toFixed(3)}</span>
                  <span className="result-unit">kWh</span>
                </div>
                <div className="result-details">
                  <span>Fator de utilização: <strong>{previsao.fator_utilizacao?.toFixed(4)}</strong></span>
                  <span>Potência ref.: <strong>{previsao.potencia_kw_ac_ref} kW</strong></span>
                </div>
              </div>
            )}
          </section>
        )}

        {/* ══ ANALISAR CSV ══ */}
        {active === "analisar" && (
          <section className="page">
            <h2 className="page-title">🔍 Análise de CSV com Modelo</h2>
            <p className="page-sub">
              Suba um CSV e o sistema aplica <strong>previsão (RandomForest)</strong> +{" "}
              <strong>detecção de anomalias (IsolationForest)</strong> em cada linha simultaneamente.
            </p>
            <div className="step-card">
              <div className={`dropzone ${arquivoAnalise ? "dropzone--selected" : ""}`}
                onClick={() => document.getElementById("f-analise").click()}>
                <span className="dropzone-icon">{arquivoAnalise ? "✅" : "🔍"}</span>
                <span className="dropzone-label">{arquivoAnalise ? arquivoAnalise.name : "Clique para selecionar um CSV para análise"}</span>
                {arquivoAnalise && <span className="dropzone-size">{(arquivoAnalise.size / 1024).toFixed(1)} KB</span>}
                <input id="f-analise" type="file" accept=".csv" style={{ display: "none" }}
                  onChange={(e) => { setArquivoAnalise(e.target.files[0]); setAnaliseResult(null); }} />
              </div>
              <div className="step-actions">
                <Btn label="Analisar CSV"     loading={isLoading("analisar")} onClick={handleAnalisar}    icon="🔍" variant="primary" />
                {analiseResult && (
                  <Btn label="Baixar resultado" loading={false} onClick={handleDownloadCSV} icon="⬇" variant="success" />
                )}
              </div>
              <div className="pipeline-badges">
                <span className="pipeline-badge pipeline-badge--blue">① RandomForest → análise kWh</span>
                <span className="pipeline-arrow">→</span>
                <span className="pipeline-badge pipeline-badge--orange">② IsolationForest → anomalia</span>
                <span className="pipeline-arrow">→</span>
                <span className="pipeline-badge pipeline-badge--green">③ resultado CSV </span>
              </div>
            </div>
            {analiseResult && (
              <>
                <div className="stats-row">
                  <Stat
                    label="Anomalias"
                    value={analiseResult.resumo?.anomalias_detectadas ?? 0}
                    sub={`${analiseResult.resumo?.percentual_anomalias ?? 0}% do total`}
                    warn
                  />
                  <Stat
                    label="Total de Linhas"
                    value={analiseResult.resumo?.total_linhas?.toLocaleString?.() ?? "0"}
                    accent
                  />
                  <Stat
                    label="Consumo Médio"
                    value={`${Number(analiseResult?.resumo?.consumo_previsto_medio_kwh ?? 0).toFixed(3)} kWh`}
                  />
                  <Stat
                    label="Consumo Total"
                    value={`${Number(analiseResult?.resumo?.consumo_previsto_total_kwh ?? 0).toFixed(1)} kWh`}
                  />
                </div>
                <div className="card">
                  <h3 className="card-title">Preview dos Resultados</h3>
                  <DataTable rows={analiseResult.preview} limit={50}
                    cols={[
                      { key: "hora",                     label: "Hora" },
                      { key: "temperatura",              label: "Temp °C" },
                      { key: "potencia_kw_ac_ref",       label: "Potência kW" },
                      { key: "consumo_kwh_previsto",     label: "Previsto kWh", render: (v) => v?.toFixed(3) },
                      { key: "fator_utilizacao_previsto",label: "Fator Util.",  render: (v) => v?.toFixed(4) },
                      { key: "anomalia_csv", label: "Anomalia",
                        render: (v) => v ? <span className="badge-anomaly">⚠ SIM</span> : <span className="badge-ok">✓ OK</span>
                      },
                    ]}
                  />
                </div>
              </>
            )}
          </section>
        )}

        {/* ══ ANOMALIAS ══ */}
        {active === "detectar" && (
          <section className="page">
            <h2 className="page-title">⚠ Anomalias do CSV Analisado</h2>
            <p className="page-sub">
              Esta tela usa somente os dados já processados em <strong>Analisar CSV</strong>,
              sem buscar nada do banco e sem reprocessar desnecessariamente.
            </p>

            <div className="step-card">
              <div className="step-actions">
                <Btn
                  label="Analisar CSV"
                  loading={isLoading("analisar")}
                  onClick={handleAnalisar}
                  icon="🔍"
                  variant="primary"
                />
                <Btn
                  label="Baixar CSV das Anomalias"
                  loading={isLoading("anomalias")}
                  onClick={handleBaixarAnomalias}
                  icon="⬇"
                  variant="success"
                />
              </div>

              <p className="step-desc" style={{ marginTop: 14 }}>
                A análise é reaproveitada automaticamente se o mesmo arquivo já tiver sido processado.
              </p>
            </div>

            {!analiseResult && !isLoading("analisar") && (
              <p className="empty" style={{ marginTop: 40 }}>
                Analise um CSV primeiro para visualizar as anomalias.
              </p>
            )}

            {analiseResult && (
              <>
                <div className="stats-row">
                  <Stat
                    label="Anomalias"
                    value={analiseResult.resumo?.anomalias_detectadas ?? 0}
                    sub={`${analiseResult.resumo?.percentual_anomalias ?? 0}% do total`}
                    warn
                  />
                  <Stat
                    label="Total de Linhas"
                    value={analiseResult.resumo?.total_linhas?.toLocaleString?.() ?? "0"}
                    accent
                  />
                </div>

                <div className="card">
                  <h3 className="card-title">
                    Registros Anômalos — {(analiseResult.anomalias || []).length} encontrados
                  </h3>

                  <DataTable
                    rows={analiseResult.anomalias || []}
                    limit={100}
                    cols={[
                      { key: "hora", label: "Hora" },
                      { key: "dia_semana", label: "Dia semana" },
                      { key: "mes", label: "Mês" },
                      { key: "temperatura", label: "Temp °C" },
                      { key: "potencia_kw_ac_ref", label: "Potência kW" },
                      {
                        key: "consumo_kwh_previsto",
                        label: "Previsto kWh",
                        render: (v) => Number(v ?? 0).toFixed(3),
                      },
                      {
                        key: "fator_utilizacao_previsto",
                        label: "Fator Util.",
                        render: (v) => Number(v ?? 0).toFixed(4),
                      },
                      {
                        key: "anomalia_csv",
                        label: "Status",
                        render: (v) =>
                          v ? (
                            <span className="badge-anomaly">⚠ ANOMALIA</span>
                          ) : (
                            <span className="badge-ok">✓ Normal</span>
                          ),
                      },
                    ]}
                  />
                </div>
              </>
            )}
          </section>
        )}

        {/* ══ DADOS — analytics ══ */}
        {active === "consumo" && (
          <DadosPage
            analiseResult={analiseResult}
            loading={isLoading("analisar")}
            onLoad={handleAnalisar}
          />
        )}
      </main>
    </>
  );
}