## Run Alembic Migrations

### Configuration

```bash
cp alembic.ini.example alembic.ini
```

- Update the `alembic.ini` with your database credentials (`sqlalchemy.url`)
  
### (Optional) Create a new migration

```bash
uv run alembic revision --autogenerate -m "Add ..."
```

### Upgrade the database

```bash
uv run alembic upgrade head
```

### Downgrade the database
```bash
uv run alembic downgrade -1
```