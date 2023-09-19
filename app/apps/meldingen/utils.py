def get_taaktypes(melding):
    from apps.meldingen.service import MeldingenService

    taakapplicaties = MeldingenService().taakapplicaties()
    taaktypes = [
        [
            tt.get("_links", {}).get("self"),
            f"{tt.get('omschrijving')}",
        ]
        for ta in taakapplicaties.get("results", [])
        for tt in ta.get("taaktypes", [])
    ]
    gebruikte_taaktypes = [
        *set(
            list(
                to.get("taaktype")
                for to in melding.get("taakopdrachten_voor_melding", [])
                if not to.get("resolutie")
            )
        )
    ]
    taaktypes = [tt for tt in taaktypes if tt[0] not in gebruikte_taaktypes]
    return taaktypes
