# 🚀 Frontend SaaS - Consultor Multi-Agentes

## Stack Recomendada

| Tecnologia | Versão | Propósito |
|------------|--------|-----------|
| **Next.js** | 14.1 | Framework React com App Router |
| **React** | 18.2 | UI Library |
| **TypeScript** | 5.3 | Type Safety |
| **TailwindCSS** | 3.4 | Styling |
| **TanStack Query** | 5.x | Data Fetching & Caching |
| **Zustand** | 4.x | State Management |
| **Axios** | 1.6 | HTTP Client |
| **Lucide React** | 0.3 | Icons |
| **Sonner** | 1.3 | Toast Notifications |
| **Recharts** | 2.x | Charts & Visualizations |

---

## 📁 Estrutura de Pastas

```
frontend/
├── src/
│   ├── app/                      # Next.js App Router
│   │   ├── (auth)/               # Grupo de rotas auth (sem layout)
│   │   │   ├── login/
│   │   │   │   └── page.tsx      # Página de login
│   │   │   └── register/
│   │   │       └── page.tsx      # Página de registro
│   │   ├── (dashboard)/          # Grupo de rotas dashboard (com layout)
│   │   │   ├── dashboard/
│   │   │   │   └── page.tsx      # Dashboard principal
│   │   │   ├── nova-analise/
│   │   │   │   └── page.tsx      # Criar nova análise
│   │   │   ├── analise/
│   │   │   │   └── [id]/
│   │   │   │       └── page.tsx  # Visualizar análise
│   │   │   ├── configuracoes/
│   │   │   │   └── page.tsx      # Configurações da conta
│   │   │   └── layout.tsx        # Layout do dashboard
│   │   ├── layout.tsx            # Layout raiz
│   │   ├── page.tsx              # Home (redireciona)
│   │   └── globals.css           # Estilos globais
│   │
│   ├── components/               # Componentes reutilizáveis
│   │   ├── ui/                   # Componentes base (Button, Input, Card...)
│   │   ├── forms/                # Formulários
│   │   ├── charts/               # Gráficos
│   │   └── providers.tsx         # Context providers
│   │
│   ├── services/                 # Integração com API
│   │   └── api-client.ts         # Cliente HTTP configurado
│   │
│   ├── stores/                   # Estado global (Zustand)
│   │   └── auth-store.ts         # Estado de autenticação
│   │
│   ├── hooks/                    # Custom hooks
│   │   ├── use-auth.ts
│   │   └── use-analyses.ts
│   │
│   └── types/                    # TypeScript types
│       └── index.ts
│
├── public/                       # Assets estáticos
├── package.json
├── next.config.js
├── tailwind.config.ts
└── tsconfig.json
```

---

## 🚀 Quick Start

```bash
cd frontend

# Instalar dependências
npm install

# Criar arquivo .env
cp .env.example .env.local

# Rodar em desenvolvimento
npm run dev
```

Acesse: http://localhost:3000

---

## ⚙️ Configuração

### `.env.local`

```env
# API Backend
NEXT_PUBLIC_API_URL=http://localhost:8000

# URL do App (para callbacks OAuth, etc)
NEXT_PUBLIC_APP_URL=http://localhost:3000

# Ambiente
NEXT_PUBLIC_ENV=development
```

---

## 📱 Páginas Implementadas

### 1. Login (`/login`)
- Formulário de email/senha
- Integração com API de autenticação
- Refresh token automático
- Redirect para dashboard após login

### 2. Dashboard (`/dashboard`)
- Cards de estatísticas
- Lista de análises recentes
- Status em tempo real
- CTA para nova análise

### 3. Nova Análise (`/nova-analise`) - A implementar
- Formulário de descrição do problema
- Seleção de tipo de negócio
- Seleção de profundidade
- Envio assíncrono

### 4. Visualizar Análise (`/analise/[id]`) - A implementar
- Sumário executivo
- Resultados por agente
- Exportação PDF

---

## 🔐 Autenticação

O sistema usa **JWT** com refresh automático:

```typescript
// services/api-client.ts

// 1. Login salva tokens em cookies
await apiClient.login(email, password);

// 2. Requests incluem token automaticamente
// Authorization: Bearer <access_token>

// 3. Em 401, refresh é feito automaticamente
// Se refresh falhar, redireciona para /login
```

---

## 🎨 UX para Retenção

### Princípios Aplicados

1. **Onboarding Progressivo**
   - Primeira análise guiada
   - Tooltips explicativos
   - Empty states informativos

2. **Feedback Imediato**
   - Loading states claros
   - Toasts de sucesso/erro
   - Progresso de análise em tempo real

3. **Valor Rápido**
   - Dashboard com métricas úteis
   - Análises recentes acessíveis
   - CTA claro para nova análise

4. **Micro-interações**
   - Animações sutis
   - Hover states
   - Transições suaves

---

## 🚢 Estratégia de Deploy

### Opção 1: Vercel (Recomendado)

```bash
# Instalar Vercel CLI
npm i -g vercel

# Deploy
vercel

# Configurar variáveis de ambiente
vercel env add NEXT_PUBLIC_API_URL
```

**Vantagens:**
- Deploy automático via Git
- Preview deployments
- Edge Functions
- Analytics integrado

### Opção 2: Docker

```dockerfile
# Dockerfile
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:20-alpine AS runner
WORKDIR /app
COPY --from=builder /app/.next/standalone ./
COPY --from=builder /app/.next/static ./.next/static
COPY --from=builder /app/public ./public

ENV NODE_ENV=production
ENV PORT=3000

EXPOSE 3000
CMD ["node", "server.js"]
```

```bash
docker build -t frontend .
docker run -p 3000:3000 --env-file .env frontend
```

### Opção 3: Netlify

```toml
# netlify.toml
[build]
  command = "npm run build"
  publish = ".next"

[[plugins]]
  package = "@netlify/plugin-nextjs"
```

---

## 📊 Checklist de Produção

- [ ] Variáveis de ambiente configuradas
- [ ] `NEXT_PUBLIC_API_URL` apontando para produção
- [ ] CORS configurado no backend
- [ ] SSL/HTTPS habilitado
- [ ] Error tracking (Sentry) configurado
- [ ] Analytics configurado
- [ ] SEO meta tags
- [ ] Open Graph images
- [ ] Favicon e PWA manifest

---

## 🧪 Testando Localmente

```bash
# 1. Inicie o backend
cd backend
uvicorn backend.app:app --reload

# 2. Inicie o frontend
cd frontend
npm run dev

# 3. Acesse http://localhost:3000/login
```
