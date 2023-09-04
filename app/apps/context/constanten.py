FILTERS = (("status",), ("begraafplaats",), ("onderwerp",), ("wijk",), ("buurt",))
FILTER_NAMEN = [f[0] for f in FILTERS]

KOLOMMEN = (
    ("msb_nummer", "MSB Nummer", "melding.meta.id"),
    # ("wijk", "Wijk", "melding.locaties_voor_melding.0.wijknaam"),
    # ("buurt", "Buurt", "melding.locaties_voor_melding.0.buurtnaam"),
)
