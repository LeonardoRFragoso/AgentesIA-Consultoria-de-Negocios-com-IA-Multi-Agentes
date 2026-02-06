# 🔧 Configuração Inicial

## Pré-requisitos

- Python 3.8+
- Conta Anthropic com API Key

## Passo 1: Obter Chave da API

1. Acesse https://console.anthropic.com/
2. Faça login ou crie uma conta
3. Vá para "API Keys"
4. Clique em "Create Key"
5. Copie a chave gerada

## Passo 2: Configurar Variável de Ambiente

### Opção A: Usando arquivo `.env` (Recomendado)

1. Na raiz do projeto, abra o arquivo `.env`
2. Substitua `ANTHROPIC_API_KEY=` pela sua chave:
   ```
   ANTHROPIC_API_KEY=sk-ant-v0-xxxxxxxxxxxxx
   ```
3. Salve o arquivo

### Opção B: Variável de Ambiente do Sistema (Windows)

**PowerShell:**
```powershell
$env:ANTHROPIC_API_KEY = "sua-chave-aqui"
```

**CMD:**
```cmd
set ANTHROPIC_API_KEY=sua-chave-aqui
```

**Permanentemente (Windows):**
1. Pressione `Win + X` e abra "System"
2. Clique em "Advanced system settings"
3. Clique em "Environment Variables"
4. Clique em "New" (em User variables)
5. Nome: `ANTHROPIC_API_KEY`
6. Valor: `sua-chave-aqui`
7. Clique OK e reinicie o terminal

## Passo 3: Instalar Dependências

```bash
pip install -r requirements.txt
```

## Passo 4: Executar a Aplicação

```bash
streamlit run app.py
```

A aplicação abrirá em `http://localhost:8501`

## Troubleshooting

### Erro: "ANTHROPIC_API_KEY não está configurada"
- Verifique se a chave foi configurada corretamente no `.env`
- Reinicie o terminal/IDE após configurar
- Certifique-se de que o arquivo `.env` está na raiz do projeto

### Erro: "Invalid API Key"
- Verifique se copiou a chave completa
- Certifique-se de que a chave não tem espaços extras
- Gere uma nova chave em https://console.anthropic.com/

### Erro: "Connection refused"
- Verifique sua conexão com internet
- Certifique-se de que a API Anthropic está acessível

## Próximos Passos

1. Digite um problema de negócio no campo de entrada
2. Clique em "🚀 Analisar Cenário"
3. Aguarde a análise dos 5 agentes
4. Revise o diagnóstico executivo consolidado
5. Baixe o relatório em Markdown se desejar

---

**Dúvidas?** Consulte o README.md para mais informações sobre o projeto.
