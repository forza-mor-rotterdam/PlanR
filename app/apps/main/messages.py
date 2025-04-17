from django.contrib.messages.storage.fallback import FallbackStorage


class FallbackDeduplicatedStorage(FallbackStorage):
    def _store(self, messages, response, *args, **kwargs):
        seen = set()
        deduplicated_messages = []
        for m in messages:
            m_hasable = (m.message, m.level)
            if m_hasable not in seen:
                seen.add(m_hasable)
                deduplicated_messages.append(m)
        return super()._store(deduplicated_messages, response, *args, **kwargs)


MELDING_LIJST_OPHALEN_ERROR = "Er ging iets mis met het ophalen van meldingen"
MELDING_OPHALEN_ERROR = "Er ging iets mis met het ophalen van de melding"
MELDING_NIET_GEVONDEN_ERROR = "De melding is niet gevonden"
MELDING_ANNULEREN_ERROR = "Er ging iets mis met het annuleren van de melding"
MELDING_ANNULEREN_SUCCESS = "De melding is geannuleerd"
MELDING_INFORMATIE_TOEVOEGEN_ERROR = (
    "Er ging iets mis met het toevoegen van de informatie"
)
MELDING_INFORMATIE_TOEVOEGEN_SUCCESS = "De informatie is toegevoegd aan de melding"
MELDING_LOCATIE_AANPASSEN_ERROR = "Er ging iets mis met het aanpassen van de locatie"
MELDING_LOCATIE_AANPASSEN_SUCCESS = "De locatie van de melding is aangepast"
MELDING_AFHANDELEN_ERROR = "Er ging iets mis met het afhandelen van de melding"
MELDING_AFHANDELEN_SUCCESS = "De melding is afgehandeld"
MELDING_HEROPENEN_ERROR = "Er ging iets mis met het heropenen van de melding"
MELDING_HEROPENEN_SUCCESS = "De melding is heropend"
MELDING_PAUZEREN_ERROR = "Er ging iets mis met het pauzeren van de melding"
MELDING_PAUZEREN_SUCCESS = "De melding is gepauzeerd"
MELDING_HERVATTEN_ERROR = "Er ging iets mis met het hervatten van de melding"
MELDING_HERVATTEN_SUCCESS = "De melding is hervat"
MELDING_URGENTIE_AANPASSEN_ERROR = "Er ging iets mis met het aanpassen van de urgentie"
MELDING_URGENTIE_AANPASSEN_SUCCESS = "De urgentie van de melding is aangepast"

TAAK_AANMAKEN_ERROR = "Er ging iets mis met het aanmaken van de taak"
TAAK_AANMAKEN_SUCCESS = "De taak is aangemaakt"
TAAK_AFRONDEN_ERROR = "Er ging iets mis met het afronden van de taak"
TAAK_AFRONDEN_SUCCESS = "De taak is afgerond"
TAAK_ANNULEREN_ERROR = "Er ging iets mis met het annuleren van de taak"
TAAK_ANNULEREN_SUCCESS = "De taak is geannuleerd"
