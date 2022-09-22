FILENAME_ALLOWED_CHARS = (
    "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_-"
)


def _replace_illegal_characters_from_iri(iri: str) -> str:
    return "".join((char if char in FILENAME_ALLOWED_CHARS else "_") for char in iri)
