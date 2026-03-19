# ⚡ PowerPredict

## 📋 Descrição da Solução

O PowerPredict é uma aplicação inteligente voltada para monitoramento e otimização do consumo de energia em instalações prediais ou industriais. O projeto coleta dados históricos de consumo energético, processa e estrutura esses dados para análise, identifica padrões e desvios de comportamento, e utiliza aprendizado supervisionado para treinar um modelo preditivo do fator de utilização. Com essas previsões, é possível planejar melhor o consumo de energia e identificar locais ou momentos de desperdício, promovendo eficiência operacional e sustentabilidade. Além disso, o projeto fornece métricas interpretáveis (como MAE, RMSE e R²) e mantém um pipeline de dados robusto que permite treinar novos modelos sempre que a base é atualizada.

- Coleta dados históricos de consumo, variáveis temporais (hora, dia, mês), fatores ambientais (temperatura), características do local (feriado, fim de semana, intensidade operacional) e indicadores de anomalias.
- Treina um modelo preditivo usando aprendizado supervisionado (Random Forest) para estimar o fator de utilização da energia.
- Permite visualizar métricas e previsões, auxiliando na tomada de decisão para eficiência energética.
- Mantém um pipeline de dados que permite atualizar a base e treinar modelos continuamente.

O PowerPredict se enquadra principalmente nos desafios **(1, 2, 3, 9 e 15)**: Análise e Exploração de Dados, Previsão e Forecasting, Detecção de Anomalias, Aprendizado Supervisionado e Sustentabilidade e Eficiência.

---

## 🔍 Problema Abordado

Muitas empresas enfrentam dificuldades em identificar desperdício de energia e padrões de consumo fora do normal. Isso pode gerar custos excessivos, falhas operacionais ou desperdício de recursos. O PowerPredict resolve este problema ao:

- Identificar padrões e tendências no consumo de energia.
- Prever o consumo futuro e o fator de utilização da energia.
- Detectar desvios anômalos de forma automática, permitindo ações corretivas.
- Fornecer métricas claras para apoiar decisões estratégicas e sustentáveis.

---

## 🛠️ Tecnologias Utilizadas

- **Backend:** Python, Django, Django REST Framework
- **Banco de Dados:** SQLite
- **Data Science / IA:** Pandas, Scikit-learn, Joblib
- **Modelos:** Random Forest Regressor (aprendizado supervisionado) / IsolationForest (anomalias)
- **Frontend:** React / JavaScript / Vite / CSS para dashboards de visualização
- **Ferramentas auxiliares:** BarChart / Git / Jupyter Notebook / Pipeline (para experimentação de modelos)

---

## 🚀 Como executar o projeto do zero

### Pré-requisitos

Certifique-se de ter instalado na sua máquina:

- [Python 3.10+](https://www.python.org/downloads/)
- [Node.js 18+](https://nodejs.org/)
- [Git](https://git-scm.com/)

---

### 1. Clonar o repositório
```bash
git clone https://github.com/Koebaptista/PowerPredict.git
cd PowerPredict
```

---

### 2. Configurar o Backend (Django)

#### 2.1 Criar e ativar o ambiente virtual
```bash
# Windows
python -m venv myenv
myenv\Scripts\activate

# Linux / Mac
python -m venv myenv
source myenv/bin/activate
```

#### 2.2 Instalar as dependências Python
```bash
pip install -r requirements.txt
```

#### 2.3 Aplicar as migrations
```bash
python manage.py makemigrations
python manage.py migrate
```
Caso de um erro no banco depois de você ter feito tudo certinho, e subido a planilha csv para treinar o modelo, rode: 

```bash
python manage.py makemigrations monitoramento
python manage.py migrate
```

#### 2.4 Iniciar o servidor Django
```bash
python manage.py runserver
```

> O backend estará rodando em **http://127.0.0.1:8000**

---

### 3. Configurar o Frontend (React)

Abra um **novo terminal** (mantenha o Django rodando no anterior).

#### 3.1 Entrar na pasta do frontend
```bash
cd frontend
```

#### 3.2 Instalar as dependências Node
```bash
npm install
```

#### 3.3 Iniciar o servidor de desenvolvimento
```bash
npm run dev
```

> O frontend estará rodando em **http://localhost:5173**

---

### ⚠️ Preparação dos dados

A base de dados original foi obtida do **Kaggle**, porém por ser insuficiente para um treinamento robusto, optamos por **simular os dados**. Para isso, execute o script abaixo — ele gerará automaticamente um CSV com aproximadamente **1568042 linhas**:
```bash
python script_simulado.py
```

> Você usará esse arquivo gerado para importar no sistema e treinar o modelo de IA com Machine Learning.

---

### 4. Usar o sistema — passo a passo

Com os dois servidores rodando, acesse **http://localhost:5173** no navegador e siga o fluxo:

#### Passo 1 — Importar o dataset

- Vá em **Preparar & Treinar**
- Clique na dropzone e selecione o arquivo CSV gerado pelo script
- Clique em **Importar Dataset**
- Aguarde a confirmação de registros importados
- Para acompanhar o processo, observe o terminal do backend

#### Passo 2 — Treinar o modelo

- Em **Preparar & Treinar**, clique em **Treinar Modelo**
- Aguarde o processamento — acompanhe no terminal do backend
- As métricas **R², MAE e RMSE** aparecerão na tela ao concluir

#### Passo 3 — Usar o modelo

A partir daqui o modelo está pronto. Você tem quatro opções:

**📈 Previsão unitária:**
- Vá em **Previsão**
- Preencha os campos (hora, temperatura, potência, etc.)
- Clique em **Calcular Previsão**

**🔍 Análise de CSV:**
- Vá em **Analisar CSV**
- Suba um novo arquivo CSV
- O sistema rodará previsão + detecção de anomalias em cada linha
- Baixe o resultado em CSV

**⚠️ Anomalias:**
- Vá em **Anomalias**
- Visualize os registros anômalos e baixe o resultado em CSV

**📊 Visualizar dados:**
- Vá em **Dados**
- Visualize gráficos e rankings, e baixe o resultado em CSV

---

### 5. Estrutura de terminais necessária
```
Terminal 1 (Backend)           Terminal 2 (Frontend)
──────────────────────         ──────────────────────
cd PowerPredict                cd PowerPredict/frontend
myenv\Scripts\activate         npm run dev
python manage.py runserver
```

---

### ⚠️ Problemas comuns

| Problema | Solução |
|----------|---------|
| `ModuleNotFoundError` | Verifique se o ambiente virtual está ativado |
| `CORS error` no frontend | Confirme que o Django está rodando na porta 8000 |
| `Modelo não encontrado` | Execute o treinamento antes de usar previsão ou análise de CSV |
| `Tabela não existe` | Rode `python manage.py migrate` novamente |
| Porta 8000 ocupada | `python manage.py runserver 8001` e atualize a URL no `api.js` |

Caso de um erro no banco depois de você ter feito tudo certinho, e subido a planilha csv para treinar o modelo, rode: 

```bash
python manage.py makemigrations monitoramento
python manage.py migrate
```

---

## 🔄 Fluxo Completo da Aplicação
```
╔══════════════════════════════════════════════════════════════╗
║                    FASE 1 — PREPARAÇÃO                       ║
╚══════════════════════════════════════════════════════════════╝

  👤 Usuário (Frontend)
       │
       │  Sobe CSV histórico
       │  (nome, tipo_local, data_hora, consumo_kwh,
       │   potencia_kw_ac_ref, temperatura, hora, etc.)
       ▼
  📄 App.jsx → api.js
       │
       │  POST /api/upload/
       ▼
  ⚙️  views.py → upload_dataset_api()
       │
       │  Lê CSV em chunks de 20.000 linhas
       │  Converte tipos, limpa nulos
       │  bulk_create() em batches de 5.000
       ▼
  🗄️  Banco de Dados (SQLite)
       │
       │  Tabela: ConsumoEnergia
       │  Campos: nome, tipo_local, data_hora,
       │          hora, mes, dia_semana, temperatura,
       │          consumo_kwh, potencia_kw_ac_ref,
       │          fim_de_semana, feriado, anomalia, ...
       ▼
  ✅  Retorna: { mensagem, total_importado }


╔══════════════════════════════════════════════════════════════╗
║                    FASE 2 — TREINAMENTO                      ║
╚══════════════════════════════════════════════════════════════╝

  👤 Usuário clica "Treinar Modelo"
       │
       │  POST /api/modelo/treinar/
       ▼
  ⚙️  views.py → treinar_modelo_api()
       │
       ▼
  🧠 services/treinamento.py → treinar_modelo()
       │
       │  1. Calcula target: fator_utilizacao =
       │       consumo_kwh / potencia_kw_ac_ref
       │  2. Features: hora, dia_semana, temperatura,
       │       mes, fim_de_semana, feriado,
       │       consumo_base_estimado,
       │       intensidade_operacional_local,
       │       sensibilidade_temperatura_local
       │  3. Split treino/teste (80/20)
       │  4. Treina RandomForestRegressor
       │       n_estimators=150, max_depth=18
       │  5. Calcula MAE, RMSE, R²
       │  6. Salva modelo serializado
       ▼
  💾 ml_models/
       ├── modelo_consumo.pkl          ← modelo treinado
       └── modelo_consumo_info.json    ← métricas + features
       │
       ▼
  ✅  Retorna: { R², MAE, RMSE, total_registros, features }


╔══════════════════════════════════════════════════════════════╗
║              FASE 3A — PREDIÇÃO UNITÁRIA                     ║
╚══════════════════════════════════════════════════════════════╝

  👤 Usuário preenche formulário de previsão
       │
       │  POST /api/prever/
       │  { hora, dia_semana, temperatura, mes,
       │    potencia_kw_ac_ref, fim_de_semana,
       │    feriado, consumo_base_estimado, ... }
       ▼
  ⚙️  views.py → prever_consumo_api()
       │
       ▼
  🧮 services/previsao.py → prever_consumo()
       │
       │  1. Carrega modelo_consumo.pkl
       │  2. Monta DataFrame com os parâmetros
       │  3. model.predict(X)
       │  4. fator_utilizacao = max(0, resultado)
       │  5. consumo_kwh = fator × potencia_kw_ac_ref
       ▼
  ✅  Retorna: { fator_utilizacao, previsao_consumo_kwh,
                 potencia_kw_ac_ref }


╔══════════════════════════════════════════════════════════════╗
║          FASE 3B — ANÁLISE DE CSV + ANOMALIAS                ║
╚══════════════════════════════════════════════════════════════╝

  👤 Usuário sobe novo CSV para análise
       │
       │  POST /api/analisar-csv/
       │  (arquivo CSV com dados novos)
       ▼
  ⚙️  views.py → analisar_csv_api()
       │
       ├──▶ services/previsao.py → prever_dataframe()
       │         │
       │         │  Para cada linha do CSV:
       │         │  1. Carrega modelo_consumo.pkl
       │         │  2. Aplica RandomForest em lote
       │         │  3. Gera: consumo_kwh_previsto
       │         │           fator_utilizacao_previsto
       │         ▼
       │
       └──▶ services/deteccao_anomalia.py
                 → detectar_anomalias_dataframe()
                     │
                     │  1. Usa fator_utilizacao_previsto
                     │     como feature principal
                     │  2. Aplica IsolationForest
                     │     contamination=0.02
                     │     n_estimators=200
                     │  3. Marca anomalia_csv = True/False
                     ▼

  📊 Consolida resultados:
       ├── resumo: total_linhas, anomalias_detectadas,
       │           percentual, consumo_medio, consumo_total
       ├── preview: primeiras 100 linhas
       ├── anomalias: apenas linhas anômalas
       ├── graficos: consumo_por_hora, consumo_por_mes,
       │            anomalias_por_dia_semana
       └── csv_resultado_base64: arquivo para download
       │
       ▼
  ✅  Retorna JSON completo → frontend renderiza
       gráficos, tabelas e disponibiliza download
```

---

## 📁 Responsabilidade de cada arquivo

### 🐍 Backend

| Arquivo | O que faz |
|---------|-----------|
| `apps/monitoramento/models.py` | Define a tabela `ConsumoEnergia` — uma linha = uma leitura horária |
| `apps/monitoramento/views.py` | Recebe requisições HTTP, valida entrada, orquestra services, devolve Response |
| `apps/monitoramento/urls.py` | Roteamento da app — mapeia cada endpoint para sua view |
| `apps/monitoramento/serializers.py` | Converte objetos Django em JSON para a API |
| `services/treinamento.py` | Treina o RandomForest, salva `.pkl` e `.json` de métricas |
| `services/previsao.py` | Previsão unitária e em lote usando o modelo salvo |
| `services/deteccao_anomalia.py` | IsolationForest no banco e em DataFrames externos |
| `services/modelo_info.py` | Lê o `.json` de métricas e retorna para o frontend |
| `services/processamento.py` | Helpers de limpeza e transformação de dados |
| `ml_models/modelo_consumo.pkl` | Modelo treinado serializado (gerado dinamicamente) |
| `ml_models/modelo_consumo_info.json` | Métricas R², MAE, RMSE, importância das features |
| `apps/monitoramento/migrations/0001_initial.py` | Migration inicial — cria a tabela no banco de dados |
| `apps/monitoramento/admin.py` | Registra os models no painel Django Admin |
| `apps/monitoramento/apps.py` | Configuração e nome da app Django |
| `apps/monitoramento/forms.py` | Formulários Django (validação server-side) |
| `apps/monitoramento/tests.py` | Testes unitários e de integração da app |
| `manage.py` | Entry point do Django — executa comandos como `runserver`, `migrate` |
| `requirements.txt` | Lista todas as dependências Python do projeto |
| `config/settings.py` | Configurações globais: banco de dados, apps instaladas, CORS, timezone |
| `config/urls.py` | Roteamento raiz — inclui as rotas de cada app |
| `config/wsgi.py` | Interface WSGI para deploy em produção |
| `config/asgi.py` | Interface ASGI para suporte a requisições assíncronas |

---

### ⚛️ Frontend

| Arquivo | O que faz |
|---------|-----------|
| `frontend/src/App.jsx` | Toda a UI: estado global, navegação, handlers e componentes |
| `frontend/src/services/api.js` | Funções de chamada HTTP para cada endpoint do backend |
| `frontend/src/App.css` | Design system dark industrial da aplicação |
| `frontend/src/index.css` | Reset e estilos base globais |
| `frontend/src/main.jsx` | Entry point React — monta o componente raiz no DOM |
| `frontend/index.html` | HTML raiz da SPA React |
| `frontend/package.json` | Dependências e scripts Node do frontend |
| `frontend/vite.config.js` | Configuração do Vite — proxy para o backend na porta 8000 |