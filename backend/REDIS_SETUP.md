# Redis Setup - Desenvolvimento vs Produção

## Resumo

- **Desenvolvimento**: Usa fallback em memória (sem Redis necessário)
- **Produção**: Requer Redis para cache, rate limiting e fila de tasks

## Desenvolvimento (Recomendado: Sem Redis)

Em desenvolvimento, a aplicação usa automaticamente:
- **Cache**: Memória RAM
- **Rate Limiting**: Memória RAM
- **Task Queue**: In-Memory Queue com ThreadPool

### Vantagens
✅ Sem dependências externas
✅ Mais rápido para testes
✅ Sem erros de conexão
✅ Ideal para desenvolvimento local

### Como rodar
```bash
# Ativar venv
.\venv\Scripts\Activate.ps1

# Rodar a aplicação
python run.py
```

Os logs mostrarão:
```
Cache initialized: Memory
RedisQueue inicializada
```

**Nota**: Erros de conexão ao Redis são suprimidos em desenvolvimento (apenas DEBUG level).

---

## Produção (Requer Redis)

### Opção 1: Docker (Recomendado)

```bash
# Iniciar Redis em container
docker run -d \
  --name redis-saas \
  -p 6379:6379 \
  -v redis-data:/data \
  redis:7-alpine \
  redis-server --appendonly yes

# Verificar se está rodando
docker ps | grep redis
```

### Opção 2: Instalação Local (Windows)

#### Via Chocolatey (requer Admin)
```powershell
# Abrir PowerShell como Administrator
choco install redis-64

# Iniciar Redis
redis-server
```

#### Via WSL2 (Recomendado para Windows)
```bash
# No WSL2
sudo apt-get update
sudo apt-get install redis-server

# Iniciar
redis-server
```

#### Via Memurai (Windows nativo)
```powershell
# Download: https://github.com/microsoftarchive/memurai-developer/releases
# Instalar e iniciar o serviço
```

### Opção 3: Cloud (AWS/Azure/Heroku)

#### AWS ElastiCache
```bash
# Criar instância Redis
aws elasticache create-cache-cluster \
  --cache-cluster-id saas-redis \
  --engine redis \
  --cache-node-type cache.t3.micro \
  --engine-version 7.0
```

#### Azure Cache for Redis
```bash
# Via Azure CLI
az redis create \
  --resource-group mygroup \
  --name saas-redis \
  --location eastus \
  --sku Basic \
  --vm-size c0
```

---

## Configuração em Produção

### 1. Variáveis de Ambiente (.env)

```env
# Ambiente
ENVIRONMENT=production

# Redis (obrigatório em produção)
REDIS_URL=redis://localhost:6379/0

# Ou com autenticação
REDIS_URL=redis://:password@redis-host:6379/0

# Ou para Azure
REDIS_URL=rediss://default:password@saas-redis.redis.cache.windows.net:6380/0
```

### 2. Verificar Conexão

```bash
# Testar conexão Redis
redis-cli ping
# Deve retornar: PONG

# Ou via Python
python -c "import redis; r = redis.from_url('redis://localhost:6379/0'); print(r.ping())"
```

### 3. Monitoramento

```bash
# Ver estatísticas Redis
redis-cli info stats

# Ver uso de memória
redis-cli info memory

# Monitorar em tempo real
redis-cli monitor
```

---

## Comportamento da Aplicação

### Em Desenvolvimento (ENVIRONMENT=development)

```python
# Logs de erro Redis são DEBUG level (não aparecem por padrão)
logger.debug(f"Worker error (development - Redis optional): {e}")

# Fallback automático para memória
Cache initialized: Memory
InMemoryQueue inicializada com 4 workers
```

### Em Produção (ENVIRONMENT=production)

```python
# Logs de erro Redis são ERROR level (aparecem sempre)
logger.error(f"Worker error: {e}")

# Falha se Redis não estiver disponível
# A aplicação não inicia sem Redis
```

---

## Checklist para Produção

- [ ] Redis instalado e rodando
- [ ] `REDIS_URL` configurada em `.env`
- [ ] Conexão testada com `redis-cli ping`
- [ ] Firewall permite porta 6379 (ou porta customizada)
- [ ] Backup de dados Redis configurado
- [ ] Monitoramento de memória Redis ativo
- [ ] `ENVIRONMENT=production` em `.env`
- [ ] Logs de erro Redis sendo monitorados

---

## Troubleshooting

### Erro: "Error 10061 connecting to localhost:6379"
**Causa**: Redis não está rodando
**Solução**: Iniciar Redis ou usar fallback em memória (desenvolvimento)

### Erro: "Connection refused"
**Causa**: Redis não está escutando na porta configurada
**Solução**: Verificar `REDIS_URL` e porta do Redis

### Erro: "WRONGPASS invalid username-password pair"
**Causa**: Autenticação Redis falhou
**Solução**: Verificar senha em `REDIS_URL`

### Redis usando muita memória
**Solução**: Configurar política de evicção
```bash
redis-cli CONFIG SET maxmemory-policy allkeys-lru
```

---

## Performance

### Benchmarks (Local)

| Operação | Memória | Redis |
|----------|---------|-------|
| Cache GET | <1ms | 1-2ms |
| Cache SET | <1ms | 2-3ms |
| Task Enqueue | <1ms | 2-3ms |
| Rate Limit Check | <1ms | 1-2ms |

### Recomendações

- **Desenvolvimento**: Use memória (mais rápido)
- **Produção**: Use Redis (distribuído, persistente)
- **Staging**: Use Redis (simular produção)

---

## Próximos Passos

1. Para desenvolvimento: Continue usando fallback em memória
2. Para produção: Configure Redis conforme sua infraestrutura
3. Monitore logs para erros de conexão
4. Configure backups Redis se usar dados persistentes
