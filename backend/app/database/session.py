# Re-exporta connect() desde migrations para mantener compatibilidad.
# La versión canónica (con PRAGMA foreign_keys = ON) vive en migrations.py.
from app.database.migrations import connect as connect  # noqa: F401
