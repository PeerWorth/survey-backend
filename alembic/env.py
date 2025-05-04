from logging.config import fileConfig
from os import getenv

from dotenv import load_dotenv
from sqlalchemy import engine_from_config, pool

from alembic import context
from app.module.asset.model import MySQLBase
from app.module.auth.model import User, UserConsent  # noqa > create table
from database.enum import EnvironmentType

load_dotenv()

ENVIRONMENT = getenv("ENVIRONMENT", None)

if ENVIRONMENT == EnvironmentType.LOCAL.value or ENVIRONMENT == EnvironmentType.TEST.value:
    ALEMBIC_MYSQL_URL = getenv("ALEMBIC_DEV_MYSQL_URL")
elif ENVIRONMENT == EnvironmentType.PROD.value:
    ALEMBIC_MYSQL_URL = getenv("ALEMBIC_PROD_MYSQL_URL")
else:
    raise ValueError(f"{ENVIRONMENT} 환경변수 설정이 잘못되었습니다.")


config = context.config

config.set_main_option("sqlalchemy.url", ALEMBIC_MYSQL_URL)
fileConfig(config.config_file_name)
target_metadata = MySQLBase.metadata


def run_migrations():
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)

        with context.begin_transaction():
            context.run_migrations()


run_migrations()
