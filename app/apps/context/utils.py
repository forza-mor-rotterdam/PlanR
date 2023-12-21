def get_gebruiker_context(gebruiker):
    if hasattr(gebruiker, "profiel") and hasattr(gebruiker.profiel, "context"):
        return gebruiker.profiel.context
    return None


def get_gebruiker_profiel(gebruiker):
    if hasattr(gebruiker, "profiel"):
        return gebruiker.profiel
    return None
