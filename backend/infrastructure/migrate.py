from alembic import command
from alembic.config import Config


def run_migrations():
    """
    Runs Alembic migrations to update the database schema.
    """
    alembic_cfg = Config("alembic.ini")

    # Explicitly set script_location relative to this ini file
    alembic_cfg.set_main_option("script_location", "alembic")

    command.upgrade(alembic_cfg, "head")