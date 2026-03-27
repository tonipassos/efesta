"""
É FESTA — Configuração do Alembic (Migrações de BD)
Arquivo: backend/alembic.ini simplificado
Execute: alembic init migrations  (primeira vez)
         alembic revision --autogenerate -m "descricao"
         alembic upgrade head
"""

# alembic.ini (conteúdo principal — salve como alembic.ini na pasta backend/)
ALEMBIC_INI = """
[alembic]
script_location = migrations
prepend_sys_path = .
sqlalchemy.url = sqlite:///./efesta.db

[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARN
handlers = console
qualname =

[logger_sqlalchemy]
level = WARN
handlers =
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers =
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S
"""

# Exemplo de como criar migrações:
COMANDOS = """
# 1. Inicializar Alembic (apenas primeira vez):
alembic init migrations

# 2. Gerar migração automática baseada nos modelos:
alembic revision --autogenerate -m "criar tabelas iniciais"

# 3. Aplicar migração:
alembic upgrade head

# 4. Ver status:
alembic current

# 5. Reverter última migração:
alembic downgrade -1
"""

if __name__ == "__main__":
    with open("alembic.ini", "w") as f:
        f.write(ALEMBIC_INI.strip())
    print("✅ alembic.ini criado!")
    print(COMANDOS)
