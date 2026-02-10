# 🧠 AgentesIA - Consultoria de Negócios com IA Multi-Agentes

[![Deploy Backend](https://img.shields.io/badge/Backend-Railway-purple)](https://railway.app)
[![Deploy Frontend](https://img.shields.io/badge/Frontend-Vercel-black)](https://vercel.com)
[![License](https://img.shields.io/badge/License-MIT-blue.svg)](LICENSE)

Plataforma SaaS de análise estratégica de negócios que utiliza múltiplos agentes de IA especializados para fornecer diagnósticos completos e acionáveis.

**🌐 Live Demo**: [agentes-ia-consultoria-de-negocios.vercel.app](https://agentes-ia-consultoria-de-negocios.vercel.app)

## 🎯 Visão Geral

O **AgentesIA** é uma plataforma completa que simula um time executivo de consultores, oferecendo:

- **Análise multi-perspectiva** de problemas de negócio
- **5 agentes especializados** trabalhando em conjunto
- **Processamento assíncrono** com Redis para alta performance
- **Exportação de relatórios** em PDF, PPTX e Markdown
- **Sistema de planos** (Free, Pro, Enterprise) com limites configuráveis
- **Multi-tenant** com isolamento por organização

## ✨ Funcionalidades Principais

### 🤖 Análise Multi-Agentes

| Agente | Especialidade |
|--------|---------------|
| � **Analista de Negócio** | Interpreta problemas e levanta hipóteses |
| 💼 **Estrategista Comercial** | Propõe ações práticas e estratégias |
| 💰 **Analista Financeiro** | Avalia viabilidade e ROI |
| 📈 **Especialista de Mercado** | Valida com benchmarks e tendências |
| 👔 **Revisor Executivo** | Consolida análises em resumo executivo |

### � Exportação de Relatórios

- **Markdown**: Formato leve e universal
- **PDF**: Formatação profissional (Pro/Enterprise)
- **PPTX**: Pronto para apresentações (Pro/Enterprise)

## 💰 Planos e Limites

| Recurso | Free | Pro (R$97/mês) | Enterprise (R$297/mês) |
|---------|------|----------------|------------------------|
| Análises/mês | 5 | 50 | Ilimitado |
| Agentes | **Escolhe 2** | Todos os 5 | Todos os 5 |
| Exportação | Markdown | PDF, PPTX, MD | Todos formatos |
| Usuários | 1 | 5 | Ilimitado |
| Histórico | 7 dias | 90 dias | 365 dias |

## 🏗️ Arquitetura

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Frontend      │────▶│   Backend       │────▶│   Claude API    │
│   (Next.js)     │     │   (FastAPI)     │     │   (Anthropic)   │
│   Vercel        │     │   Railway       │     │                 │
└─────────────────┘     └────────┬────────┘     └─────────────────┘
                                 │
                    ┌────────────┼────────────┐
                    ▼            ▼            ▼
             ┌──────────┐ ┌──────────┐ ┌──────────┐
             │PostgreSQL│ │  Redis   │ │  Redis   │
             │  (DB)    │ │ (Cache)  │ │ (Queue)  │
             └──────────┘ └──────────┘ └──────────┘
```

## 🚀 Como Executar

### Pré-requisitos
- Python 3.11+
- Node.js 18+
- Redis (opcional para desenvolvimento)
- Chave de API da Anthropic

### 1. Clone o repositório
```bash
git clone https://github.com/LeonardoRFragoso/AgentesIA-Consultoria-de-Negocios-com-IA-Multi-Agentes.git
cd AgentesIA-Consultoria-de-Negocios-com-IA-Multi-Agentes
```

### 2. Configure o Backend
```bash
cd backend

# Crie ambiente virtual
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Instale dependências
pip install -r requirements.txt

# Configure variáveis de ambiente
cp .env.example .env
# Edite .env e adicione sua ANTHROPIC_API_KEY

# Inicie o servidor
python -m uvicorn app:app --reload --port 8000
```

### 3. Configure o Frontend
```bash
cd frontend

# Instale dependências
npm install

# Configure variáveis de ambiente
cp .env.example .env.local
# Adicione: NEXT_PUBLIC_API_URL=http://localhost:8000

# Inicie o servidor de desenvolvimento
npm run dev
```

### 4. Acesse a aplicação
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/health

## 📁 Estrutura do Projeto

```
├── backend/                    # API FastAPI
│   ├── app.py                  # Aplicação principal
│   ├── config.py               # Configurações
│   ├── agents/                 # Agentes de IA
│   │   ├── analyst.py
│   │   ├── commercial.py
│   │   ├── financial.py
│   │   ├── market.py
│   │   └── reviewer.py
│   ├── api/                    # Endpoints REST
│   │   ├── auth.py             # Autenticação JWT
│   │   ├── analyses.py         # CRUD de análises
│   │   ├── async_analyses.py   # Análises assíncronas
│   │   └── billing.py          # Planos e limites
│   ├── core/                   # Lógica central
│   │   ├── agent.py            # Classe base de agentes
│   │   └── types.py            # Tipos e modelos
│   ├── database/               # Modelos e conexão
│   ├── infrastructure/         # Cache, Queue, Logging
│   ├── orchestrator/           # Orquestração de agentes
│   ├── prompts/                # Prompts dos agentes (.md)
│   ├── security/               # Auth e JWT
│   ├── services/               # Lógica de negócio
│   ├── team/                   # BusinessTeam wrapper
│   └── Dockerfile
│
├── frontend/                   # Next.js 14
│   ├── src/
│   │   ├── app/                # App Router
│   │   ├── components/         # Componentes React
│   │   └── services/           # API client
│   └── package.json
│
├── docs/                       # Documentação
└── docker-compose.yml          # Deploy local
```

## 💡 Exemplos de Uso

### Exemplo 1: Queda de Vendas
```
"Nossas vendas caíram 20% nos últimos 3 meses. 
Qual pode ser a causa e como devemos responder?"
```

### Exemplo 2: Expansão de Mercado
```
"Estamos considerando expandir para o mercado europeu. 
Quais são os principais riscos e oportunidades?"
```

### Exemplo 3: Retenção de Clientes (com arquivo anexo)
```
Problema: "Nosso churn aumentou de 5% para 8% ao mês."
Anexo: churn_dados.xlsx
```

## 🔄 Fluxo de Funcionamento

```
1. Usuário descreve problema de negócio
   ↓
2. Sistema valida plano e agentes disponíveis
   ↓
3. Task enfileirada no Redis
   ↓
4. Agentes executam em paralelo (DAG)
   ↓
5. Revisor consolida análises
   ↓
6. Resultado salvo no banco
   ↓
7. Usuário visualiza diagnóstico executivo
   ↓
8. Exportar relatório (Pro/Enterprise)
```

## 🛠️ Tecnologias

### Backend
- **Framework**: FastAPI + Gunicorn
- **IA**: Claude 3 (Anthropic)
- **Banco de dados**: PostgreSQL
- **Cache/Queue**: Redis
- **Autenticação**: JWT (PyJWT + bcrypt)
- **Exportação**: ReportLab (PDF), python-pptx (PPTX)

### Frontend
- **Framework**: Next.js 14 (App Router)
- **UI**: Tailwind CSS + Framer Motion
- **Componentes**: Lucide Icons
- **HTTP**: Axios
- **Deploy**: Vercel

### Infraestrutura
- **Backend**: Railway
- **Frontend**: Vercel
- **Database**: Railway PostgreSQL
- **Cache**: Redis Cloud

## 📝 Variáveis de Ambiente

### Backend (.env)
```env
ENVIRONMENT=development
ANTHROPIC_API_KEY=sk-ant-xxxxx
JWT_SECRET_KEY=sua-chave-jwt-secreta
DATABASE_URL=postgresql://user:pass@host:5432/db
REDIS_URL=redis://localhost:6379  # opcional em dev
CORS_ORIGINS=["http://localhost:3000"]
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## � Deploy em Produção

### Railway (Backend)
1. Conecte o repositório
2. Configure Root Directory: `backend`
3. Adicione PostgreSQL
4. Configure variáveis de ambiente
5. Deploy automático via Git

### Vercel (Frontend)
1. Importe o repositório
2. Configure Root Directory: `frontend`
3. Adicione `NEXT_PUBLIC_API_URL` apontando para Railway
4. Deploy automático

## 🐳 Docker (Local)

```bash
# Build e run completo
docker-compose up --build

# Apenas backend
docker-compose up backend

# Apenas frontend  
docker-compose up frontend
```

## 📄 Licença

Este projeto é fornecido como está para fins educacionais e de portfólio.

## 🤝 Contribuições

Contribuições são bem-vindas! Sinta-se livre para:
- Melhorar prompts dos agentes
- Adicionar novos agentes especializados
- Otimizar a interface
- Implementar novos formatos de exportação
- Sugerir novos recursos

## � Autor

**Leonardo Fragoso**
- GitHub: [@LeonardoRFragoso](https://github.com/LeonardoRFragoso)

---

**Desenvolvido com ❤️ para análise estratégica de negócios**
