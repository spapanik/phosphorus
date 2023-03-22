import re


def canonicalise_name(name: str) -> str:
    return re.sub(r"[-_.]+", "-", name).lower()
