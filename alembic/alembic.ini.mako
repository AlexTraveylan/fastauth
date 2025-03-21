# Configuration for FastAuth with asynchronous PostgreSQL

[alembic]
# path to migration scripts.
# Use forward slashes (/) also on windows to provide an os agnostic path
script_location = ${script_location}

# template used to generate migration file names
file_template = %%(year)d%%(month).2d%%(day).2d_%%(hour).2d%%(minute).2d%%(second).2d_%%(slug)s

# sys.path path, will be prepended to sys.path if present.
# defaults to the current working directory.
prepend_sys_path = .

# timezone to use when rendering the date within the migration file
# as well as the filename.
timezone = UTC

# max length of characters to apply to the "slug" field
truncate_slug_length = 40

# set to 'true' to run the environment during
# the 'revision' command, regardless of autogenerate
revision_environment = false

# set to 'true' to allow .pyc and .pyo files without
# a source .py file to be detected as revisions in the
# versions/ directory
sourceless = false

# version location specification; This defaults
# to ${script_location}/versions.  When using multiple version
# directories, initial revisions must be specified with --version-path.
version_locations = %(here)s/versions

# version path separator; As mentioned above, this is the character used to split
# version_locations. The default within new alembic.ini files is "os", which uses os.pathsep.
version_path_separator = os

# the output encoding used when revision files
# are written from script.py.mako
output_encoding = utf-8

# PostgreSQL connection URL
sqlalchemy.url = postgresql+asyncpg://postgres:postgres@localhost:5432/fastauth

[post_write_hooks]
# post_write_hooks defines scripts or Python functions that are run
# on newly generated revision scripts.  See the documentation for further
# detail and examples

# lint with attempts to fix using "ruff" - use the exec runner, execute a binary
hooks = ruff
ruff.type = exec
ruff.executable = %(here)s/.venv/bin/ruff
ruff.options = check --fix REVISION_SCRIPT_FILENAME

# Logging configuration
[loggers]
keys = root,sqlalchemy,alembic

[handlers]
keys = console

[formatters]
keys = generic

[logger_root]
level = WARNING
handlers = console
qualname = root

[logger_sqlalchemy]
level = WARNING
handlers = console
qualname = sqlalchemy.engine

[logger_alembic]
level = INFO
handlers = console
qualname = alembic

[handler_console]
class = StreamHandler
args = (sys.stderr,)
level = NOTSET
formatter = generic

[formatter_generic]
format = %(levelname)-5.5s [%(name)s] %(message)s
datefmt = %H:%M:%S