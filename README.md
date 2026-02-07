# 🧠 AgentesIA - Consultoria de Negócios com IA Multi-Agentes

Plataforma SaaS de análise estratégica de negócios que utiliza múltiplos agentes de IA especializados para fornecer diagnósticos completos e acionáveis.

## 🎯 Visão Geral

O **AgentesIA** é uma plataforma completa que simula um time executivo de consultores, oferecendo:

- **Análise multi-perspectiva** de problemas de negócio
- **5 agentes especializados** trabalhando em conjunto
- **Upload de arquivos** (CSV, Excel, PDF) para análise contextualizada
- **Consultor IA Contínuo** - chat de follow-up pós-análise
- **Exportação de relatórios** em PDF, DOCX e PPTX
- **Sistema de planos** (Free, Pro, Enterprise) com limites configuráveis

## ✨ Funcionalidades Principais

### � Análise Multi-Agentes
| Agente | Especialidade |
|--------|---------------|
| 🔍 **Analista de Negócio** | Interpreta problemas e levanta hipóteses |
| 💼 **Estrategista Comercial** | Propõe ações práticas e estratégias |
| 💰 **Analista Financeiro** | Avalia viabilidade e ROI |
| � **Especialista de Mercado** | Valida com benchmarks e tendências |
| 👔 **Revisor Executivo** | Consolida análises em decisão final |

### � Consultor IA Contínuo (Novo!)
Continue a conversa após a análise para:
- Aprofundar pontos específicos
- Esclarecer dúvidas
- Refinar estratégias
- A IA já conhece seu contexto e dados

### 📎 Upload de Arquivos
Anexe dados para análise contextualizada:
- **CSV/TXT**: Extração completa de texto
- **Excel (.xlsx)**: Leitura de até 3 abas, 50 linhas
- **PDF**: Extração de até 10 páginas

### 📥 Exportação de Relatórios
Exporte análises completas (incluindo chat de refino):
- **PDF**: Formatação profissional
- **DOCX**: Editável no Word
- **PPTX**: Pronto para apresentações

## 💰 Planos e Limites

| Recurso | Free | Pro (R$99/mês) | Enterprise (R$299/mês) |
|---------|------|----------------|------------------------|
| Análises/mês | 5 | 50 | Ilimitado |
| Agentes | 3 | 5 | 5 |
| Perguntas de refino/análise | 3 | 20 | Ilimitado |
| Exportação PDF | ❌ | ✅ | ✅ |
| Exportação DOCX/PPTX | ❌ | ❌ | ✅ |

## 🚀 Como Executar

### Pré-requisitos
- Python 3.10+
- Node.js 18+
- Chave de API da Anthropic

### 1. Clone o repositório
```bash
git clone https://github.com/LeonardoRFragoso/Agente-Multi-Agentes-de-Negocio-com-Streamlit.git
cd Agente-Multi-Agentes-de-Negocio-com-Streamlit
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
python -m uvicorn main:app --reload --port 8000
```

### 3. Configure o Frontend
```bash
cd frontend

# Instale dependências
npm install

# Configure variáveis de ambiente
cp .env.example .env.local

# Inicie o servidor de desenvolvimento
npm run dev
```

### 4. Acesse a aplicação
- **Frontend**: http://localhost:3000
- **API Docs**: http://localhost:8000/docs

## 📁 Estrutura do Projeto

```
agentesia/
├── backend/                    # API FastAPI
│   ├── main.py                 # Endpoints principais
│   ├── agents/                 # Agentes de IA
│   │   ├── analyst.py
│   │   ├── commercial.py
│   │   ├── financial.py
│   │   ├── market.py
│   │   └── reviewer.py
│   ├── core/                   # Lógica central
│   │   ├── agent.py            # Classe base de agentes
│   │   ├── types.py            # Tipos e modelos
│   │   └── exceptions.py
│   ├── orchestrator/           # Orquestração de agentes
│   │   ├── orchestrator.py
│   │   └── dag.py              # Resolução de dependências
│   ├── prompts/                # Prompts dos agentes
│   └── requirements.txt
│
├── frontend/                   # Next.js + React
│   ├── src/
│   │   ├── app/                # Páginas (App Router)
│   │   │   ├── (auth)/         # Login/Register
│   │   │   ├── (dashboard)/    # Dashboard protegido
│   │   │   │   ├── dashboard/
│   │   │   │   ├── nova-analise/
│   │   │   │   ├── analise/[id]/
│   │   │   │   └── billing/
│   │   │   └── page.tsx        # Landing page
│   │   ├── components/         # Componentes React
│   │   ├── services/           # API client
│   │   └── stores/             # Estado global (Zustand)
│   └── package.json
│
├── docs/                       # Documentação
└── docker-compose.yml          # Deploy com Docker
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
1. Usuário descreve problema + anexa arquivos (opcional)
   ↓
2. Sistema extrai conteúdo dos arquivos
   ↓
3. Analista interpreta e levanta hipóteses
   ↓
4. Comercial propõe estratégias
   ↓
5. Financeiro avalia viabilidade (Pro/Enterprise)
   ↓
6. Mercado valida contexto (Pro/Enterprise)
   ↓
7. Revisor consolida análises
   ↓
8. Diagnóstico executivo é exibido
   ↓
9. Usuário pode refinar com perguntas de follow-up
   ↓
10. Exportar relatório completo (Pro/Enterprise)
```

## 🎨 Interface

### Landing Page
- Hero com proposta de valor
- Destaque do recurso "Consultor IA Contínuo"
- Features e benefícios
- Planos e preços

### Dashboard
- Lista de análises recentes
- Status em tempo real (pending, running, completed)
- Acesso rápido a nova análise

### Página de Análise
- Visualização por agente (abas)
- Chat de refino com contador de uso
- Exportação em múltiplos formatos
- Animação de loading com carrossel de agentes

## �️ Tecnologias

### Backend
- **Framework**: FastAPI
- **IA**: Claude (Anthropic) via API
- **Autenticação**: JWT
- **PDF**: ReportLab
- **DOCX**: python-docx
- **PPTX**: python-pptx
- **Excel**: openpyxl
- **PDF Reader**: PyPDF2

### Frontend
- **Framework**: Next.js 14 (App Router)
- **UI**: Tailwind CSS
- **Componentes**: Lucide Icons
- **Estado**: Zustand
- **HTTP**: Axios
- **Notificações**: Sonner

## 📈 Roadmap

- [x] ~~Integração com dados reais (CSV, Excel, PDF)~~
- [x] ~~Exportação em PDF, DOCX, PPTX~~
- [x] ~~Chat de refino pós-análise~~
- [x] ~~Sistema de planos e limites~~
- [x] ~~Containerização com Docker~~
- [ ] Integração com Mercado Pago (pagamentos)
- [ ] Memória de longo prazo por empresa
- [ ] Histórico de análises persistente
- [ ] Modo comparativo (cenário A vs B)
- [ ] Deploy em produção

## 🛠️ Troubleshooting

### Erro: "ANTHROPIC_API_KEY not found"
```bash
# Verifique o arquivo .env no backend
cat backend/.env
# Deve conter: ANTHROPIC_API_KEY=sk-ant-...
```

### Erro: "Module not found"
```bash
cd backend
pip install -r requirements.txt
```

### Frontend não conecta ao backend
```bash
# Verifique se o backend está rodando na porta 8000
# E se o frontend tem NEXT_PUBLIC_API_URL=http://localhost:8000
```

## 📝 Variáveis de Ambiente

### Backend (.env)
```env
ANTHROPIC_API_KEY=sk-ant-xxxxx
SECRET_KEY=sua-chave-jwt-secreta
DATABASE_URL=sqlite:///./agentesia.db
```

### Frontend (.env.local)
```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

## � Docker

```bash
# Build e run
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
