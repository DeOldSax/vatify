uvicorn main:app --reload


pytest -v test_validate_vat.py

# Alembic migrations

- init: alembic init migrations
- erste revision erzeugen: alembic revision --autogenerate -m "init schema"
- migration anwenden: alembic upgrade head

# alembic workflow bei änderungen
- models anpassen, neue revision erzeugen:
- alembic revision --autogenerate -m "added field xyz"
- anwenden: alembic upgrade head

