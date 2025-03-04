import re
from enum import Enum
from typing import Annotated

import typer


class _Version(str, Enum):
    major = "major"
    minor = "minor"
    patch = "patch"


app = typer.Typer()


@app.command()
def bump(
    version: Annotated[_Version, typer.Argument(help="The version to bump")],
) -> None:
    """Bumps the version of the project.

    Open the pyproject.toml file and update the version field.
    Use it before commit or in CI/CD pipeline.

    Arguments
    ---------
    version : _Version
        The version to bump.

    Raises
    ------
    ValueError
        If the version field is not found in the pyproject.toml file.
    """
    with open("pyproject.toml", "r") as f:
        text = f.read()

    version_match = re.search(r'version = "([^"]+)"', text)

    if not version_match:
        raise ValueError("Version field not found in pyproject.toml")

    current_version = version_match.group(1)
    major, minor, patch = map(int, current_version.split("."))

    match version:
        case _Version.major:
            new_version = f"{major + 1}.0.0"
        case _Version.minor:
            new_version = f"{major}.{minor + 1}.0"
        case _Version.patch:
            new_version = f"{major}.{minor}.{patch + 1}"

    text = text.replace(current_version, new_version)

    with open("pyproject.toml", "w") as f:
        f.write(text)


if __name__ == "__main__":
    app()
