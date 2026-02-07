#!/usr/bin/env python
"""
Script para testar autenticação do backend.
Executa testes básicos de signup, login e acesso protegido.

Uso:
    python test_auth.py
"""

import os
import sys

# Configura ambiente de desenvolvimento
os.environ.setdefault("ENVIRONMENT", "development")
os.environ.setdefault("DATABASE_URL", "sqlite:///./test_auth.db")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret-key-for-development-only-32-chars")

from fastapi.testclient import TestClient


def main():
    print("=" * 60)
    print("🧪 TESTE DE AUTENTICAÇÃO - Backend SaaS")
    print("=" * 60)
    print()
    
    # Importa app após configurar ambiente
    from backend.app import app
    
    client = TestClient(app)
    
    # =========================================================================
    # TESTE 1: Health Check
    # =========================================================================
    print("1️⃣ Testando Health Check...")
    response = client.get("/health")
    assert response.status_code == 200, f"Health check falhou: {response.text}"
    print(f"   ✅ Status: {response.json()['status']}")
    print()
    
    # =========================================================================
    # TESTE 2: Registro de Usuário
    # =========================================================================
    print("2️⃣ Testando Registro de Usuário...")
    register_data = {
        "email": "teste@exemplo.com",
        "password": "SenhaSegura123!",
        "organization_name": "Empresa Teste",
        "name": "Usuário Teste"
    }
    
    response = client.post("/api/v1/auth/register", json=register_data)
    
    if response.status_code == 201:
        tokens = response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        print(f"   ✅ Registro bem-sucedido!")
        print(f"   📦 Access Token: {access_token[:50]}...")
        print(f"   📦 Refresh Token: {refresh_token[:50]}...")
    elif response.status_code == 400 and "já está em uso" in response.text:
        print(f"   ⚠️ Usuário já existe, fazendo login...")
        # Faz login se usuário já existe
        login_data = {
            "email": register_data["email"],
            "password": register_data["password"]
        }
        response = client.post("/api/v1/auth/login", json=login_data)
        assert response.status_code == 200, f"Login falhou: {response.text}"
        tokens = response.json()
        access_token = tokens["access_token"]
        refresh_token = tokens["refresh_token"]
        print(f"   ✅ Login bem-sucedido!")
    else:
        print(f"   ❌ Registro falhou: {response.status_code}")
        print(f"   {response.text}")
        sys.exit(1)
    print()
    
    # =========================================================================
    # TESTE 3: Login
    # =========================================================================
    print("3️⃣ Testando Login...")
    login_data = {
        "email": "teste@exemplo.com",
        "password": "SenhaSegura123!"
    }
    
    response = client.post("/api/v1/auth/login", json=login_data)
    assert response.status_code == 200, f"Login falhou: {response.text}"
    tokens = response.json()
    access_token = tokens["access_token"]
    print(f"   ✅ Login bem-sucedido!")
    print()
    
    # =========================================================================
    # TESTE 4: Acesso a Rota Protegida (/me)
    # =========================================================================
    print("4️⃣ Testando Acesso a Rota Protegida...")
    headers = {"Authorization": f"Bearer {access_token}"}
    
    response = client.get("/api/v1/auth/me", headers=headers)
    assert response.status_code == 200, f"Acesso negado: {response.text}"
    user = response.json()
    print(f"   ✅ Acesso autorizado!")
    print(f"   👤 Usuário: {user['email']}")
    print(f"   🏢 Organização: {user['organization_name']}")
    print(f"   🎫 Plano: {user['plan']}")
    print()
    
    # =========================================================================
    # TESTE 5: Refresh Token
    # =========================================================================
    print("5️⃣ Testando Refresh Token...")
    refresh_data = {"refresh_token": refresh_token}
    
    response = client.post("/api/v1/auth/refresh", json=refresh_data)
    assert response.status_code == 200, f"Refresh falhou: {response.text}"
    new_tokens = response.json()
    print(f"   ✅ Token renovado com sucesso!")
    print(f"   📦 Novo Access Token: {new_tokens['access_token'][:50]}...")
    print()
    
    # =========================================================================
    # TESTE 6: Acesso sem Token (deve falhar)
    # =========================================================================
    print("6️⃣ Testando Acesso sem Token...")
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403, f"Deveria retornar 403: {response.status_code}"
    print(f"   ✅ Acesso negado corretamente (403)")
    print()
    
    # =========================================================================
    # TESTE 7: Login com Senha Errada
    # =========================================================================
    print("7️⃣ Testando Login com Senha Errada...")
    wrong_login = {
        "email": "teste@exemplo.com",
        "password": "SenhaErrada123!"
    }
    
    response = client.post("/api/v1/auth/login", json=wrong_login)
    assert response.status_code == 401, f"Deveria retornar 401: {response.status_code}"
    print(f"   ✅ Login negado corretamente (401)")
    print()
    
    # =========================================================================
    # RESULTADO
    # =========================================================================
    print("=" * 60)
    print("✅ TODOS OS TESTES PASSARAM!")
    print("=" * 60)
    print()
    print("📝 Para testar manualmente, use os comandos curl abaixo:")
    print()
    print("# Registrar:")
    print('curl -X POST http://localhost:8000/api/v1/auth/register \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"email": "user@example.com", "password": "Senha123!", "organization_name": "Minha Empresa"}\'')
    print()
    print("# Login:")
    print('curl -X POST http://localhost:8000/api/v1/auth/login \\')
    print('  -H "Content-Type: application/json" \\')
    print('  -d \'{"email": "user@example.com", "password": "Senha123!"}\'')
    print()
    print("# Acessar rota protegida:")
    print('curl http://localhost:8000/api/v1/auth/me \\')
    print('  -H "Authorization: Bearer SEU_ACCESS_TOKEN"')
    print()


if __name__ == "__main__":
    main()
