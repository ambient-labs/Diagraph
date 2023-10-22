from pathlib import Path


def get_filetype(filepath: str | Path, filetype: str | None = None):
    if filetype in ["json", "pickle"]:
        return filetype
    return "json" if str(filepath).endswith(".json") else "pickle"
