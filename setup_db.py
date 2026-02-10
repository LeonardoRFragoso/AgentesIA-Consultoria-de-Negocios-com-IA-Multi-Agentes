#!/usr/bin/env python
"""Setup PostgreSQL database for development."""

import psycopg2
from psycopg2 import sql
import sys

# Tenta diferentes configurações de conexão
configs = [
    # Sem senha (trust authentication)
    {'dbname': 'postgres', 'user': 'postgres', 'host': '127.0.0.1', 'port': 5432},
    # Com senha padrão
    {'dbname': 'postgres', 'user': 'postgres', 'password': 'postgres', 'host': '127.0.0.1', 'port': 5432},
    # Localhost IPv6
    {'dbname': 'postgres', 'user': 'postgres', 'host': 'localhost', 'port': 5432},
]

conn = None
for config in configs:
    try:
        print(f"Tentando conectar com: {config}")
        conn = psycopg2.connect(**config)
        print("✓ Conectado com sucesso!")
        break
    except psycopg2.OperationalError as e:
        print(f"✗ Falha: {e}")
        continue

if not conn:
    print("\n❌ Não foi possível conectar ao PostgreSQL")
    print("Certifique-se de que:")
    print("1. PostgreSQL está rodando")
    print("2. Usuário 'postgres' existe")
    print("3. A autenticação está configurada corretamente")
    sys.exit(1)

try:
    conn.autocommit = True
    cur = conn.cursor()
    
    # Criar banco de dados
    print("\nCriando banco de dados 'multiagentes'...")
    cur.execute("CREATE DATABASE multiagentes")
    print("✓ Banco de dados criado")
    
    # Conectar ao novo banco
    conn.close()
    config['dbname'] = 'multiagentes'
    conn = psycopg2.connect(**config)
    conn.autocommit = True
    cur = conn.cursor()
    
    # Criar extensões necessárias
    print("Criando extensões...")
    try:
        cur.execute("CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\"")
        print("✓ Extensões criadas")
    except:
        print("⚠ Extensão uuid-ossp não disponível (opcional)")
    
    print("\n✅ Banco de dados configurado com sucesso!")
    print(f"   Conexão: postgresql://postgres@127.0.0.1:5432/multiagentes")
    
except Exception as e:
    print(f"\n❌ Erro ao configurar banco: {e}")
    sys.exit(1)
finally:
    if conn:
        conn.close()
