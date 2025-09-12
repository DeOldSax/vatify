uvicorn main:app --reload

# start with ssl
uvicorn main:app \
  --host 0.0.0.0 --port 8000 \
  --ssl-certfile /mnt/c/Users/mail/localhost+2.pem \
  --ssl-keyfile  /mnt/c/Users/mail/localhost+2-key.pem


pytest -v test_validate_vat.py

# Alembic migrations

- init: alembic init migrations
- erste revision erzeugen: alembic revision --autogenerate -m "init schema"
- migration anwenden: alembic upgrade head

# alembic workflow bei änderungen
- models anpassen, neue revision erzeugen:
- alembic revision --autogenerate -m "added field xyz"
- anwenden: alembic upgrade head

