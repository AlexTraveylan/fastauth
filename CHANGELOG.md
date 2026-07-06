# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- `get_async_session` no longer converts `HTTPException`s raised by services into `DatabaseException` (409). Invalid or expired tokens now return 401 as intended, so clients can distinguish auth failures from database errors. Only `SQLAlchemyError`s are wrapped into a 409 now. The test suite exercises the real dependency through the app (new `tests/test_database.py`); the previous conftest override had masked the divergence.

## [0.6.0] - 2026-06-26

### Added
- Google OAuth2 login flow: `/api/v1/auth/google/login` and `/api/v1/auth/google/callback`. The callback creates or links the user, derives the username from the Google first name (falling back to the email), appends a short random suffix on username collision, and redirects to the frontend with the access and refresh tokens in the URL fragment.
- `FRONTEND_URL` setting (where the callback redirects the browser back).
- `given_name` field on the `GoogleUserInfo` schema.

### Changed
- `GoogleUserInfo` now tolerates missing `name`, `family_name` and `email_verified` (only `email` and `sub` are required).

## [0.5.0] - 2026-04-11

### Changed
- Migrated user IDs from `int` to `UUID` (uuid4)
- Renamed `DATABASE_URL` to `FASTAUTH_POSTGRES_POOLER_CONNECTION_STRING`
- `/register` endpoint now returns a `Token` (access + refresh) instead of `UserResponse`
- CORS allowed origins are now configurable via `ALLOWED_ORIGINS` env variable (comma-separated)

### Added
- `UserResponse` now includes the `id` field (UUID)
- Auto-conversion from `postgresql://` to `postgresql+asyncpg://` in the DB engine
- SSL support and disabled prepared statement cache (Supabase pooler compatibility)

### Fixed
- Correct typing in `Repository`: `id_: Any`, `user_id: UUID`
- Use of `col()` for SQLModel query filters

## [0.4.0] - 2025-03-14
- Added Google OAuth2 support
- Removed tests for repository
- Removed tests for database
- Async support

## [0.3.0] - 2025-03-10
- Added repository pattern
- Added tests for repository
- Added tests for database

## [0.2.0] - 2025-03-06
- Added User and Token models
- Added configuration for asynchronous PostgreSQL
- Added pydantic-settings for configuration
- Added alembic for migrations
- Added docker-compose for development

## [0.1.0] - 2025-03-05
- Initialization of the project
- Basic project configuration
- Initial project structure
