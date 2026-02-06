# 🧠 Consultor de Negócios Multi-Agentes com Streamlit

Um sistema de análise estratégica de negócios que simula um time executivo completo, utilizando múltiplos agentes de IA para fornecer diagnósticos estruturados e acionáveis.

## 🎯 Visão Geral

Este projeto implementa uma arquitetura multi-agentes que permite:

- **Análise estruturada** de problemas de negócio em linguagem natural
- **Perspectivas complementares** de 5 especialistas virtuais
- **Validação cruzada** entre agentes para coerência
- **Diagnóstico executivo** consolidado e priorizado
- **Interface intuitiva** via Streamlit

## 👥 Time de Agentes

1. **🔍 Analista de Negócio**: Interpreta problemas e levanta hipóteses
2. **💼 Estrategista Comercial**: Propõe ações práticas e estratégias
3. **💰 Analista Financeiro**: Avalia viabilidade e ROI
4. **📊 Especialista de Mercado**: Valida com benchmarks e tendências
5. **👔 Revisor Executivo**: Consolida análises em decisão final

## 🚀 Como Usar

### Instalação

```bash
# Clone ou navegue até o diretório do projeto
cd "Agente Multi-Agentes de Negócio com Streamlit"

# Instale as dependências
pip install -r requirements.txt
```

### Configuração de API Key

O projeto utiliza Claude AI (Anthropic). Configure sua chave de API:

```bash
# Windows (PowerShell)
$env:ANTHROPIC_API_KEY = "sua-chave-aqui"

# Windows (CMD)
set ANTHROPIC_API_KEY=sua-chave-aqui

# Linux/Mac
export ANTHROPIC_API_KEY="sua-chave-aqui"
```

Obtenha sua chave em: https://console.anthropic.com/

### Executar a Aplicação

```bash
streamlit run app.py
```

A aplicação abrirá em `http://localhost:8501`

## 📁 Estrutura do Projeto

```
agente-multi-agentes/
├── app.py                      # Interface Streamlit
├── requirements.txt            # Dependências
├── README.md                   # Este arquivo
│
├── agents/                     # Módulos de agentes
│   ├── __init__.py
│   ├── analyst.py              # Análise de negócio
│   ├── commercial.py           # Estratégia comercial
│   ├── financial.py            # Análise financeira
│   ├── market.py               # Contexto de mercado
│   └── reviewer.py             # Consolidação executiva
│
├── team/                       # Orquestração
│   ├── __init__.py
│   └── business_team.py        # Coordenação de agentes
│
├── prompts/                    # Instruções de sistema
│   ├── analyst.md
│   ├── commercial.md
│   ├── financial.md
│   ├── market.md
│   └── reviewer.md
│
└── utils/                      # Utilitários
    ├── __init__.py
    └── formatting.py           # Formatação de saída
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

### Exemplo 3: Retenção de Clientes
```
"Nosso churn aumentou de 5% para 8% ao mês. 
Como podemos reverter essa tendência?"
```

## 🔄 Fluxo de Funcionamento

```
1. Usuário descreve problema
   ↓
2. Analista interpreta e levanta hipóteses
   ↓
3. Comercial propõe estratégias
   ↓
4. Financeiro avalia viabilidade
   ↓
5. Mercado valida contexto
   ↓
6. Revisor consolida análises
   ↓
7. Diagnóstico executivo é exibido
```

## 🎨 Interface Streamlit

- **Sidebar**: Configurações (tipo de negócio, profundidade de análise)
- **Área Principal**: Campo de entrada e resultados
- **Abas Expansíveis**: Análises detalhadas por agente
- **Seção Executiva**: Diagnóstico consolidado em destaque
- **Download**: Exportar relatório em Markdown

## 📊 Saídas

### Diagnóstico Executivo
- Síntese do problema
- Análise de coerência entre agentes
- Recomendação estratégica
- Plano de ação consolidado
- Métricas de sucesso
- Riscos críticos
- Próximos passos (30 dias)

### Análises Detalhadas
Cada agente fornece sua perspectiva estruturada:
- Hipóteses e validações
- Ações recomendadas
- Estimativas de impacto
- Riscos e oportunidades

## 🔧 Customização

### Modificar Prompts
Edite os arquivos em `prompts/` para ajustar o comportamento dos agentes:
- Estilo de resposta
- Foco de análise
- Nível de detalhe

### Adicionar Novos Agentes
1. Crie `agents/novo_agente.py`
2. Implemente função com padrão similar aos existentes
3. Adicione prompt em `prompts/novo_agente.md`
4. Integre em `team/business_team.py`

### Mudar Modelo de IA
Edite o `model` em cada arquivo de agente:
```python
model="claude-3-5-sonnet-20241022"  # Altere para outro modelo
```

## 📈 Roadmap

- [ ] Integração com dados reais (CSV, Excel, Google Sheets)
- [ ] Memória de longo prazo por empresa
- [ ] Histórico de análises
- [ ] Modo comparativo (cenário A vs B)
- [ ] Exportação em PDF
- [ ] Deploy em Streamlit Cloud
- [ ] Containerização com Docker

## 🛠️ Troubleshooting

### Erro: "ANTHROPIC_API_KEY not found"
- Verifique se a variável de ambiente está configurada
- Reinicie o terminal após configurar

### Erro: "Module not found"
- Certifique-se de estar no diretório correto
- Reinstale dependências: `pip install -r requirements.txt`

### Respostas lentas
- Modelos de IA podem levar alguns segundos
- Verifique sua conexão com internet

## 📝 Notas Técnicas

- **Modelo**: Claude 3.5 Sonnet (Anthropic)
- **Framework Web**: Streamlit
- **Linguagem**: Python 3.8+
- **Arquitetura**: Multi-agentes com orquestração sequencial

## 💼 Casos de Uso

- Diagnóstico estratégico de negócios
- Validação de hipóteses comerciais
- Análise de cenários
- Suporte a decisões executivas
- Educação em estratégia de negócios
- Prototipagem de ideias

## 📄 Licença

Este projeto é fornecido como está para fins educacionais e de portfólio.

## 🤝 Contribuições

Sinta-se livre para:
- Melhorar prompts
- Adicionar novos agentes
- Otimizar a interface
- Sugerir novos recursos

## 📞 Suporte

Para dúvidas ou sugestões, consulte a documentação dos prompts em `prompts/` ou ajuste conforme necessário.

---

**Desenvolvido com ❤️ para análise estratégica de negócios**
