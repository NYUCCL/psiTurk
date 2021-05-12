import pytest

def test_migrate_db():
    from psiturk.db import migrate_db
    migrate_db()
