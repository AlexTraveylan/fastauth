

## Database

### Env

```
FASTAUTH_POSTGRES_POOLER_CONNECTION_STRING=postgresql://postgres.<project_id>:<password>@aws-0-eu-west-1.pooler.supabase.com:5432/postgres
```

> **Important** : utiliser le **session pooler (port 5432)**, pas le transaction pooler (port 6543).
> asyncpg utilise le protocole "prepared statement" que pgbouncer en mode transaction ne supporte pas.

### Créer les tables

Les tables sont gérées via **Alembic**. Deux façons de les créer :

#### Option 1 — Via le SQL Editor de Supabase (recommandé)

Générer le SQL sans connexion à la base :

```bash
uv run alembic upgrade head --sql
```

Copier le SQL généré et le coller dans le **SQL Editor** de Supabase.

#### Option 2 — Via connexion directe (hors pgbouncer)

Utiliser l'URL de connexion directe Supabase (pas le pooler, port 5432 avec hostname `db.<project>.supabase.co`) :

```bash
FASTAUTH_POSTGRES_POOLER_CONNECTION_STRING="postgresql://postgres:<password>@db.<project>.supabase.co:5432/postgres" \
  uv run alembic upgrade head
```

#### Futures migrations

```bash
# Générer une migration depuis les changements de modèles
uv run alembic revision --autogenerate -m "description"

# Appliquer les migrations (SQL Editor)
uv run alembic upgrade head --sql

# Rollback
uv run alembic downgrade -1
```

### Connection

```bash
psql -h localhost -p 5432 -U postgres -d fastauth
```

### Tables

```bash
# Lister les tables
\dt  # doit afficher users et tokens

# Users
SELECT * FROM users;

# Tokens
SELECT * FROM tokens;

# Vider toutes les tables
DELETE FROM tokens;
DELETE FROM users;
```
