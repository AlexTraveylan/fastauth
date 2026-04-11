

## Database

### Env

FASTAUTH_POSTGRES_POOLER_CONNECTION_STRING
postgresql://postgres.<project_id>:<password>@aws-0-eu-west-1.pooler.supabase.com:6543/postgres

### Connection

```bash
psql -h localhost -p 5432 -U postgres -d fastauth
```

### Tables

```bash
# List all tables
\dt  # should be users and tokens

# Users
SELECT * FROM users;

# Tokens
SELECT * FROM tokens;

# Delete all data from all tables
DELETE FROM tokens;
DELETE FROM users;
```
