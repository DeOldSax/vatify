from logging.config import fileConfig
from sqlalchemy import engine_from_config, pool
from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context

# --- importiere dein Projekt ---
from db.models import Base
from core.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
fileConfig(config.config_file_name)

# set target metadata for 'autogenerate'
target_metadata = Base.metadata

# wir nutzen dein DATABASE_URL aus settings
DATABASE_URL = str(settings.DATABASE_URL)


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = DATABASE_URL
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()

def do_run_migrations(sync_connection):
    """Wird in einem synchronen Kontext ausgeführt."""
    context.configure(connection=sync_connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    connectable = create_async_engine(DATABASE_URL, poolclass=pool.NullPool)

    async def async_main():
        async with connectable.connect() as connection:
            # führe do_run_migrations synchron auf der Verbindung aus
            await connection.run_sync(do_run_migrations)

    import asyncio
    asyncio.run(async_main())

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
