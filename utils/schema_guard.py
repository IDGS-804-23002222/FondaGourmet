from sqlalchemy import text

from models import db


def asegurar_columnas(table_name, columns):
    """Ensure columns exist in the current database table.

    Args:
        table_name: Target table name.
        columns: Iterable of tuples (column_name, sql_definition).
    """
    for column_name, sql_definition in columns:
        exists = db.session.execute(
            text(
                """
                SELECT COUNT(*)
                FROM information_schema.columns
                WHERE table_schema = DATABASE()
                  AND table_name = :table_name
                  AND column_name = :column_name
                """
            ),
            {"table_name": table_name, "column_name": column_name},
        ).scalar()

        if int(exists or 0) == 0:
            db.session.execute(
                text(f"ALTER TABLE {table_name} ADD COLUMN {column_name} {sql_definition}")
            )
