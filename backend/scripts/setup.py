"""
Script de setup para desenvolvimento local.
Cria banco de dados e usuário admin inicial.
"""

import os
import sys
import secrets

# Adiciona diretório pai ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()


def generate_jwt_secret():
    """Gera um JWT secret seguro."""
    return secrets.token_hex(32)


def check_env():
    """Verifica variáveis de ambiente obrigatórias."""
    required = ["ANTHROPIC_API_KEY", "JWT_SECRET_KEY", "DATABASE_URL"]
    missing = []
    
    for var in required:
        if not os.getenv(var):
            missing.append(var)
    
    if missing:
        print("❌ Variáveis de ambiente faltando:")
        for var in missing:
            if var == "JWT_SECRET_KEY":
                print(f"   {var} - Gere com: {generate_jwt_secret()}")
            else:
                print(f"   {var}")
        return False
    
    print("✅ Variáveis de ambiente OK")
    return True


def init_database():
    """Inicializa banco de dados com tabelas."""
    from database.connection import init_db
    
    print("📦 Inicializando banco de dados...")
    init_db()
    print("✅ Tabelas criadas")


def create_admin_user(email: str, password: str, org_name: str):
    """Cria usuário administrador inicial."""
    from database.connection import get_db_session
    from services.user_service import UserService
    
    with get_db_session() as db:
        user_service = UserService(db)
        
        # Verifica se já existe
        existing = user_service.get_user_by_email(email)
        if existing:
            print(f"⚠️  Usuário {email} já existe")
            return
        
        org, user = user_service.create_organization(
            name=org_name,
            owner_email=email,
            owner_password=password
        )
        
        print(f"✅ Organização criada: {org.name} (ID: {org.id})")
        print(f"✅ Usuário admin criado: {user.email}")


def main():
    print("=" * 60)
    print("🚀 Setup do Backend SaaS - Consultor Multi-Agentes")
    print("=" * 60)
    print()
    
    # Verifica ambiente
    if not check_env():
        print()
        print("Configure as variáveis no arquivo .env e tente novamente.")
        sys.exit(1)
    
    print()
    
    # Inicializa banco
    init_database()
    
    print()
    
    # Cria admin se solicitado
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--admin-email", help="Email do admin inicial")
    parser.add_argument("--admin-password", help="Senha do admin")
    parser.add_argument("--org-name", help="Nome da organização")
    args = parser.parse_args()
    
    if args.admin_email and args.admin_password and args.org_name:
        create_admin_user(args.admin_email, args.admin_password, args.org_name)
    else:
        print("ℹ️  Para criar usuário admin, execute:")
        print("   python scripts/setup.py --admin-email admin@example.com --admin-password senha123 --org-name 'Minha Empresa'")
    
    print()
    print("=" * 60)
    print("✅ Setup concluído!")
    print()
    print("Para iniciar o servidor:")
    print("   uvicorn backend.app:app --reload")
    print()
    print("API disponível em: http://localhost:8000")
    print("Documentação: http://localhost:8000/docs")
    print("=" * 60)


if __name__ == "__main__":
    main()
