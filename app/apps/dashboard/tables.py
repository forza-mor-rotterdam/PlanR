import logging
import statistics

from apps.main.constanten import PDOK_WIJKEN
from apps.main.templatetags.date_tags import seconds_to_human

logger = logging.getLogger(__name__)


def average(lst):
    try:
        return statistics.mean([li for li in lst if not li == 0])
    except Exception:
        ...
    return 0


def get_aantallen_tabs(meldingen, signalen, ticks=[], onderwerp=None, wijk=None):
    labels = [t.get("label") for t in ticks]

    alle_wijken = [wijk.get("wijknaam") for wijk in PDOK_WIJKEN]
    wijken = [wijk.get("wijknaam") for wijk in PDOK_WIJKEN]
    wijken_noord = [
        wijk.get("wijknaam") for wijk in PDOK_WIJKEN if wijk.get("stadsdeel") == "Noord"
    ]
    wijken_zuid = [
        wijk.get("wijknaam") for wijk in PDOK_WIJKEN if wijk.get("stadsdeel") == "Zuid"
    ]
    tabs = (
        [
            {
                "wijken": [],
                "wijk_not_in": True,
                "titel": "Heel Rotterdam",
            },
            {
                "wijken": wijken_noord,
                "wijk_not_in": False,
                "titel": "Rotterdam noord",
            },
            {
                "wijken": wijken_zuid,
                "wijk_not_in": False,
                "titel": "Rotterdam zuid",
            },
            {
                "wijken": wijken,
                "wijk_not_in": True,
                "titel": "Onbekend of buiten Rotterdam",
            },
        ]
        if not wijk
        else [
            {
                "wijken": [w for w in alle_wijken if wijk == w],
                "wijk_not_in": False,
                "titel": wijk,
            }
        ]
    )

    tabs = [
        {
            **tab,
            **{
                "datasets": [
                    {
                        "type": "line",
                        "label": "Aantal meldingen",
                        "bron": meldingen,
                    },
                    {
                        "type": "bar",
                        "label": "Aantal signalen",
                        "bron": signalen,
                    },
                ]
            },
        }
        for tab in tabs
    ]

    tabs = [
        {
            "titel": tab.get("titel"),
            "labels": labels,
            "datasets": [
                {
                    "type": dataset.get("type"),
                    "label": dataset.get("label"),
                    "barPercentage": "0.5",
                    "borderColor": "#00811F",
                    "fill": True,
                    "backgroundColor": "rgba(0,200,100,0.1)",
                    "data": [
                        sum(
                            [
                                d.get("count")
                                for d in dag
                                if bool(d.get("wijk") in tab.get("wijken"))
                                != bool(tab.get("wijk_not_in"))
                                and (not onderwerp or onderwerp == d.get("onderwerp"))
                            ]
                        )
                        for dag in dataset.get("bron")
                    ],
                }
                for dataset in tab.get("datasets", [])
            ],
        }
        for tab in tabs
    ]
    tabs = [
        {
            **tab,
            **{
                "aantallen": [
                    sum(dataset.get("data", [])) for dataset in tab.get("datasets", [])
                ]
            },
        }
        for tab in tabs
    ]
    return tabs


def get_meldingen_nieuw_vs_afgehandeld_tabs(
    meldingen, afgehandeld, ticks=[], onderwerp=None, wijk=None
):
    labels = [t.get("label") for t in ticks]

    alle_wijken = [wijk.get("wijknaam") for wijk in PDOK_WIJKEN]
    wijken = [wijk.get("wijknaam") for wijk in PDOK_WIJKEN]
    wijken_noord = [
        wijk.get("wijknaam") for wijk in PDOK_WIJKEN if wijk.get("stadsdeel") == "Noord"
    ]
    wijken_zuid = [
        wijk.get("wijknaam") for wijk in PDOK_WIJKEN if wijk.get("stadsdeel") == "Zuid"
    ]
    tabs = (
        [
            {
                "wijken": [],
                "wijk_not_in": True,
                "titel": "Heel Rotterdam",
            },
            {
                "wijken": wijken_noord,
                "wijk_not_in": False,
                "titel": "Rotterdam noord",
            },
            {
                "wijken": wijken_zuid,
                "wijk_not_in": False,
                "titel": "Rotterdam zuid",
            },
            {
                "wijken": wijken,
                "wijk_not_in": True,
                "titel": "Onbekend of buiten Rotterdam",
            },
        ]
        if not wijk
        else [
            {
                "wijken": [w for w in alle_wijken if wijk == w],
                "wijk_not_in": False,
                "titel": wijk,
            }
        ]
    )

    def afgehandeld_in_tijdsvak(t, tab):
        afgehandeld_data = [
            d.get("melding_aantal")
            for d in afgehandeld[t]
            if bool(d.get("wijk") in tab.get("wijken")) != bool(tab.get("wijk_not_in"))
            and (not onderwerp or onderwerp == d.get("onderwerp"))
        ]
        return sum(afgehandeld_data)

    def nieuw_in_tijdsvak(t, tab):
        meldingen_data = [
            d.get("count")
            for d in meldingen[t]
            if bool(d.get("wijk") in tab.get("wijken")) != bool(tab.get("wijk_not_in"))
            and (not onderwerp or onderwerp == d.get("onderwerp"))
        ]
        return sum(meldingen_data)

    tabs = [
        {
            **tab,
            **{
                "labels": labels,
                "datasets": [
                    {
                        "type": "line",
                        "label": "Aantal meldingen",
                        "borderColor": "#00811F",
                        "backgroundColor": "rgba(0,200,100,0.1)",
                        "fill": {
                            "target": "origin",
                            "below": "rgba(200, 0, 0, .1)",
                            "above": "rgba(0,200,100,0.1)",
                        },
                        "data": [
                            afgehandeld_in_tijdsvak(t, tab) - nieuw_in_tijdsvak(t, tab)
                            for t in range(0, len(labels))
                        ],
                    },
                ],
            },
        }
        for tab in tabs
    ]

    # print(json.dumps(tabs, indent=4))
    tabs = [
        {
            **tab,
            **{
                "aantal": sum(
                    [
                        sum([d for d in dataset.get("data", [])])
                        for dataset in tab.get("datasets", [])
                    ]
                )
            },
        }
        for tab in tabs
    ]
    return tabs


def get_status_veranderingen_tabs(veranderingen, ticks=[], onderwerp=None, wijk=None):
    labels = [t.get("label") for t in ticks]

    [wijk.get("wijknaam") for wijk in PDOK_WIJKEN]
    tabs = [
        {
            "begin_status": "openstaand",
            "eind_status": "in_behandeling",
            "titel": "Openstaand -> in behandeling",
        },
        {
            "begin_status": "in_behandeling",
            "eind_status": "controle",
            "titel": "In behandeling -> controle",
        },
        {
            "begin_status": "controle",
            "eind_status": "afgehandeld",
            "titel": "Controle -> afgehandeld",
        },
    ]

    # print(veranderingen)
    tabs = [
        {
            **tab,
            **{
                "datasets": [
                    {
                        "type": "line",
                        "label": "gemiddelde duur",
                        "bron": veranderingen,
                    },
                ]
            },
        }
        for tab in tabs
    ]
    # print(json.dumps(tabs, indent=4))

    tabs = [
        {
            "titel": tab.get("titel"),
            "labels": labels,
            "datasets": [
                {
                    "type": dataset.get("type"),
                    "label": dataset.get("label"),
                    "barPercentage": "0.2",
                    "borderColor": "#00811F",
                    "fill": True,
                    "backgroundColor": "rgba(0,200,100,0.1)",
                    "data": [
                        average(
                            [
                                float(d.get("duur_seconden_gemiddeld"))
                                for d in dag
                                if d.get("begin_status") == tab.get("begin_status")
                                and d.get("eind_status") == tab.get("eind_status")
                                and (not onderwerp or onderwerp == d.get("onderwerp"))
                                and (not wijk or wijk == d.get("wijk"))
                            ]
                        )
                        for dag in dataset.get("bron")
                    ],
                }
                for dataset in tab.get("datasets", [])
            ],
        }
        for tab in tabs
    ]

    tabs = [
        {
            **tab,
            **{
                "aantal": int(
                    average(
                        [
                            average([d for d in dataset.get("data", []) if d != 0])
                            for dataset in tab.get("datasets", [])
                        ]
                    )
                )
            },
        }
        for tab in tabs
    ]
    return tabs


def get_afgehandeld_tabs(afgehandeld, ticks=[], onderwerp=None, wijk=None):
    labels = [t.get("label") for t in ticks]

    alle_wijken = [wijk.get("wijknaam") for wijk in PDOK_WIJKEN]
    wijken_noord = [
        wijk.get("wijknaam") for wijk in PDOK_WIJKEN if wijk.get("stadsdeel") == "Noord"
    ]
    wijken_zuid = [
        wijk.get("wijknaam") for wijk in PDOK_WIJKEN if wijk.get("stadsdeel") == "Zuid"
    ]

    import json

    logger.info(json.dumps(afgehandeld, indent=4))

    afgehandeld = (
        [
            [variant for variant in tijdsvak if variant.get("wijk") == wijk]
            for tijdsvak in afgehandeld
        ]
        if wijk
        else afgehandeld
    )
    afgehandeld = (
        [
            [variant for variant in tijdsvak if variant.get("onderwerp") == onderwerp]
            for tijdsvak in afgehandeld
        ]
        if onderwerp
        else afgehandeld
    )

    tabs = (
        [
            {
                "wijken": [],
                "wijk_not_in": True,
                "titel": "Heel Rotterdam",
            },
            {
                "wijken": wijken_noord,
                "wijk_not_in": False,
                "titel": "Rotterdam noord",
            },
            {
                "wijken": wijken_zuid,
                "wijk_not_in": False,
                "titel": "Rotterdam zuid",
            },
        ]
        if not wijk
        else [
            {
                "wijken": [w for w in alle_wijken if wijk == w],
                "wijk_not_in": False,
                "titel": wijk,
            }
        ]
    )
    tabs = [
        {
            **tab,
            **{
                "datasets": [
                    {
                        "backgroundColor": "#00580c",
                        "label": "Midoffice",
                        "statussen": [
                            "openstaand_duur_gemiddeld",
                            "controle_duur_gemiddeld",
                        ],
                        "bron": afgehandeld,
                    },
                    {
                        "backgroundColor": "#00811f",
                        "label": "Uitvoer",
                        "statussen": [
                            "in_behandeling_duur_gemiddeld",
                        ],
                        "bron": afgehandeld,
                    },
                    {
                        "backgroundColor": "#e3f4dd",
                        "label": "Wachten",
                        "statussen": [
                            "wachten_melder_duur_gemiddeld",
                            "pauze_duur_gemiddeld",
                        ],
                        "bron": afgehandeld,
                    },
                    {
                        "backgroundColor": "#eeeeee",
                        "label": "Afgehandeld",
                        "statussen": [
                            "geannuleerd_duur_gemiddeld",
                            "afgehandeld_duur_gemiddeld",
                        ],
                        "bron": afgehandeld,
                    },
                ]
            },
        }
        for tab in tabs
    ]

    def tijdsvak_status_gemiddelden(tijdsvak, statussen, tab, dag_index):
        status_gemiddelden_totaal = []
        for status in statussen:
            status_gemiddelden = []
            for d in tijdsvak:
                if (
                    bool(d.get("wijk") in tab.get("wijken")) != tab.get("wijk_not_in")
                    and d.get(status) is not None
                ):
                    status_gemiddelden = status_gemiddelden + [
                        float(d.get(status)) for i in range(0, d.get("melding_aantal"))
                    ]
            status_gemiddelden_totaal.append(average(status_gemiddelden))
        return sum(status_gemiddelden_totaal)

    tabs = [
        {
            "titel": tab.get("titel"),
            "labels": labels,
            "type": "bar",
            "datasets": [
                {
                    "type": "bar",
                    "label": dataset.get("label"),
                    "backgroundColor": dataset.get("backgroundColor"),
                    "borderColor": "#ffffff",
                    "fill": True,
                    "data": [
                        tijdsvak_status_gemiddelden(
                            dag, dataset.get("statussen", []), tab, i
                        )
                        for i, dag in enumerate(dataset.get("bron"))
                    ],
                }
                for dataset in tab.get("datasets", [])
            ],
        }
        for tab in tabs
    ]

    def get_average(tbl):
        l2 = list(zip(*tbl))
        l2t = [sum([nn for nn in dd]) for dd in l2]
        l2tt = [d for d in l2t if d != 0]
        return average(l2tt)

    for tab in tabs:
        tab["aantal"] = get_average(
            [
                [d for d in dataset.get("data", [])]
                for dataset in tab.get("datasets", [])
            ]
        )
    return tabs


def top_vijf_aantal_meldingen_wijk(meldingen, valide_wijken, onderwerp=None, aantal=5):
    meldingen_aantal = sum(
        [sum([d.get("count") for d in kolom]) for kolom in meldingen]
    )
    meldingen_aantal = (
        sum(
            [
                sum([d.get("count") for d in kolom if d.get("onderwerp") == onderwerp])
                for kolom in meldingen
            ]
        )
        if onderwerp
        else meldingen_aantal
    )
    meldingen = (
        [[d for d in kolom if d.get("onderwerp") == onderwerp] for kolom in meldingen]
        if onderwerp
        else meldingen
    )

    wijken = [
        {
            "label": wijk,
            "aantal": sum(
                [
                    d.get("count")
                    for kolom in meldingen
                    for d in kolom
                    if d.get("wijk") == wijk
                ]
            ),
        }
        for wijk in valide_wijken
    ]
    wijken = sorted(
        [
            {
                **wijk,
                **{
                    "percentage": int(
                        float(wijk.get("aantal") / meldingen_aantal) * 100
                    ),
                    "bar": int(float(wijk.get("aantal") / meldingen_aantal) * 100),
                },
            }
            for wijk in wijken
        ],
        key=lambda b: b.get("aantal"),
        reverse=True,
    )
    aantal_meldingen_wijk = {
        "title": "Wijken met de meeste meldingen",
        "head": ["Wijk", "Aantal", "%"],
        "head_percentages": [65, 20, 15],
        "body": wijken[:aantal] if aantal else wijken,
    }
    return aantal_meldingen_wijk


def top_vijf_aantal_meldingen_onderwerp(
    meldingen, valide_onderwerpen, wijk=None, aantal=5
):
    meldingen_aantal = sum(
        [sum([d.get("count") for d in kolom]) for kolom in meldingen]
    )
    meldingen_aantal = (
        sum(
            [
                sum([d.get("count") for d in kolom if d.get("wijk") == wijk])
                for kolom in meldingen
            ]
        )
        if wijk
        else meldingen_aantal
    )
    meldingen = (
        [[d for d in kolom if d.get("wijk") == wijk] for kolom in meldingen]
        if wijk
        else meldingen
    )
    onderwerpen = [
        {
            "label": onderwerp,
            "aantal": sum(
                [
                    d.get("count")
                    for kolom in meldingen
                    for d in kolom
                    if d.get("onderwerp") == onderwerp
                ]
            ),
        }
        for onderwerp in valide_onderwerpen
    ]
    onderwerpen = sorted(
        [
            {
                **onderwerp,
                **{
                    "percentage": int(
                        float(onderwerp.get("aantal") / meldingen_aantal) * 100
                    ),
                    "bar": int(float(onderwerp.get("aantal") / meldingen_aantal) * 100),
                },
            }
            for onderwerp in onderwerpen
        ],
        key=lambda b: b.get("aantal"),
        reverse=True,
    )
    aantal_meldingen_onderwerp = {
        "title": "Meest gemelde onderwerpen",
        "head": ["Onderwerp", "Aantal", "%"],
        "head_percentages": [65, 20, 15],
        "body": onderwerpen[:aantal] if aantal else onderwerpen,
    }
    return aantal_meldingen_onderwerp


def top_vijf_aantal_onderwerpen_ontdubbeld(
    meldingen, signalen, valide_onderwerpen, wijk=None, aantal=5
):
    meldingen = (
        [[d for d in kolom if d.get("wijk") == wijk] for kolom in meldingen]
        if wijk
        else meldingen
    )
    signalen = (
        [[d for d in kolom if d.get("wijk") == wijk] for kolom in signalen]
        if wijk
        else signalen
    )

    def get_verhouding(_signalen, _meldingen, _onderwerp):
        _signalen_aantal = sum(
            [
                d.get("count")
                for kolom in _signalen
                for d in kolom
                if d.get("onderwerp") == _onderwerp
            ]
        )
        _meldingen_aantal = sum(
            [
                d.get("count")
                for kolom in _meldingen
                for d in kolom
                if d.get("onderwerp") == _onderwerp
            ]
        )
        if _meldingen_aantal <= 0:
            return float(1)
        return float(_signalen_aantal / _meldingen_aantal)

    onderwerpen_ontdubbeld = sorted(
        [
            {
                "label": onderwerp,
                "aantal": "{:.2f}".format(
                    get_verhouding(signalen, meldingen, onderwerp)
                ),
            }
            for onderwerp in valide_onderwerpen
        ],
        key=lambda b: b.get("aantal"),
        reverse=True,
    )

    def get_bar_percentage(_onderwerp, _onderwerpen):
        if float(_onderwerp.get("aantal")) <= 0:
            return 1
        aantal = float(_onderwerp.get("aantal")) - 1
        max = (float(_onderwerpen[0].get("aantal")) - 1) if _onderwerpen else 0
        if max <= 0:
            return 1
        percentage = int(float(aantal / max) * 80)
        if percentage <= 0:
            return 1
        return percentage

    onderwerpen_ontdubbeld = [
        {**onderwerp, **{"bar": get_bar_percentage(onderwerp, onderwerpen_ontdubbeld)}}
        for onderwerp in onderwerpen_ontdubbeld
    ]
    aantal_onderwerpen_ontdubbeld = {
        "title": "Meest ontdubbelde onderwerpen",
        "head": ["Onderwerp", "verhouding"],
        "head_percentages": [80, 20],
        "body": onderwerpen_ontdubbeld[:aantal] if aantal else onderwerpen_ontdubbeld,
    }
    return aantal_onderwerpen_ontdubbeld


def top_doorlooptijden_per_onderwerp(
    afgehandeld, valide_onderwerpen, wijk=None, fase=None, aantal=5
):
    statussen_per_fase = {
        "Midoffice": [
            "openstaand_duur_gemiddeld",
            "controle_duur_gemiddeld",
        ],
        "Uitvoer": [
            "in_behandeling_duur_gemiddeld",
        ],
        "Wachten": [
            "wachten_melder_duur_gemiddeld",
            "pauze_duur_gemiddeld",
        ],
        "Afgehandeld": [
            "geannuleerd_duur_gemiddeld",
            "afgehandeld_duur_gemiddeld",
        ],
    }

    alle_statussen = [
        status for f, statussen in statussen_per_fase.items() for status in statussen
    ]
    fase = None if fase not in list(statussen_per_fase.keys()) else fase
    statussen = statussen_per_fase[fase] if fase else alle_statussen

    def tijdsvak_status_gemiddelden(_afgehandeld, onderwerp, _statussen):
        status_gemiddelden_totaal = []
        for i, tijdsvak in enumerate(_afgehandeld):
            melding_aantal = 0
            tijdsvak_total = []
            for status in _statussen:
                status_gemiddelden = []
                for d in tijdsvak:
                    if onderwerp == d.get("onderwerp") and d.get(status) is not None:
                        melding_aantal += d.get("melding_aantal")
                        status_gemiddelden = status_gemiddelden + [
                            float(d.get(status))
                            for i in range(0, d.get("melding_aantal"))
                        ]
                tijdsvak_total.append(average(status_gemiddelden))
            status_gemiddelden_totaal = status_gemiddelden_totaal + [
                sum(tijdsvak_total) for i in range(0, melding_aantal)
            ]
        return average(status_gemiddelden_totaal)

    afgehandeld = (
        [
            [variant for variant in tijdsvak if variant.get("wijk") == wijk]
            for tijdsvak in afgehandeld
        ]
        if wijk
        else afgehandeld
    )
    onderwerpen = sorted(
        [
            {
                "label": onderwerp,
                "aantal": tijdsvak_status_gemiddelden(
                    afgehandeld, onderwerp, statussen
                ),
                "totaal_aantal": tijdsvak_status_gemiddelden(
                    afgehandeld, onderwerp, alle_statussen
                ),
            }
            for onderwerp in valide_onderwerpen
        ],
        key=lambda b: b.get("aantal"),
        reverse=True,
    )

    onderwerpen = [
        {
            "label": onderwerp.get("label"),
            "aantal": seconds_to_human(onderwerp.get("aantal")),
            # "percentage": round(
            #     float(onderwerp.get("aantal") / onderwerp.get("totaal_aantal")) * 100
            # )
            # if onderwerp.get("totaal_aantal")
            # else 0,
            "bar": round(
                float(onderwerp.get("aantal") / onderwerpen[0].get("aantal")) * 100
            )
            if onderwerpen and onderwerpen[0].get("aantal")
            else 0,
        }
        for onderwerp in onderwerpen
    ]

    title = f"Fase '{fase}'" if fase else "Totaal voor onderwerpen"

    doorlooptijden_per_onderwerp = {
        "title": title,
        "head": ["Onderwerp", "Duur"],
        "head_percentages": [65, 35],
        "body": onderwerpen[:aantal] if aantal else onderwerpen,
    }
    return doorlooptijden_per_onderwerp


def top_doorlooptijden_per_wijk(
    afgehandeld, valide_wijken, onderwerp=None, fase=None, aantal=5
):
    statussen_per_fase = {
        "Midoffice": [
            "openstaand_duur_gemiddeld",
            "controle_duur_gemiddeld",
        ],
        "Uitvoer": [
            "in_behandeling_duur_gemiddeld",
        ],
        "Wachten": [
            "wachten_melder_duur_gemiddeld",
            "pauze_duur_gemiddeld",
        ],
        "Afgehandeld": [
            "geannuleerd_duur_gemiddeld",
            "afgehandeld_duur_gemiddeld",
        ],
    }

    alle_statussen = [
        status for f, statussen in statussen_per_fase.items() for status in statussen
    ]
    fase = None if fase not in list(statussen_per_fase.keys()) else fase
    statussen = statussen_per_fase[fase] if fase else alle_statussen

    def tijdsvak_status_gemiddelden(_afgehandeld, wijk, _statussen):
        status_gemiddelden_totaal = []
        for i, tijdsvak in enumerate(_afgehandeld):
            melding_aantal = 0
            tijdsvak_total = []
            for status in _statussen:
                status_gemiddelden = []
                for d in tijdsvak:
                    if wijk == d.get("wijk") and d.get(status) is not None:
                        melding_aantal += d.get("melding_aantal")
                        status_gemiddelden = status_gemiddelden + [
                            float(d.get(status))
                            for i in range(0, d.get("melding_aantal"))
                        ]
                tijdsvak_total.append(average(status_gemiddelden))
            status_gemiddelden_totaal = status_gemiddelden_totaal + [
                sum(tijdsvak_total) for i in range(0, melding_aantal)
            ]
        return average(status_gemiddelden_totaal)

    afgehandeld = (
        [
            [variant for variant in tijdsvak if variant.get("onderwerp") == onderwerp]
            for tijdsvak in afgehandeld
        ]
        if onderwerp
        else afgehandeld
    )
    wijken = sorted(
        [
            {
                "label": wijk,
                "aantal": tijdsvak_status_gemiddelden(afgehandeld, wijk, statussen),
                "totaal_aantal": tijdsvak_status_gemiddelden(
                    afgehandeld, wijk, alle_statussen
                ),
            }
            for wijk in valide_wijken
        ],
        key=lambda b: b.get("aantal"),
        reverse=True,
    )

    wijken = [
        {
            "label": wijk.get("label"),
            "aantal": seconds_to_human(wijk.get("aantal")),
            # "percentage": round(
            #     float(wijk.get("aantal") / wijk.get("totaal_aantal")) * 100
            # )
            # if wijk.get("totaal_aantal")
            # else 0,
            "bar": round(float(wijk.get("aantal") / wijken[0].get("aantal")) * 100)
            if wijken and wijken[0].get("aantal")
            else 0,
        }
        for wijk in wijken
    ]

    title = f"Fase '{fase}'" if fase else "Totaal voor wijken"

    doorlooptijden_per_wijk = {
        "title": title,
        "head": ["Wijk", "Duur"],
        "head_percentages": [65, 35],
        "body": wijken[:aantal] if aantal else wijken,
    }
    return doorlooptijden_per_wijk


def top_taaktype_aantallen(
    taaktype_aantallen_per_melding, onderwerp=None, wijk=None, aantal=5
):
    taaktype_aantallen_per_melding = [
        tt
        for tijdsvak in taaktype_aantallen_per_melding
        for tt in tijdsvak
        if (not onderwerp or tt.get("onderwerp") == onderwerp)
        and (not wijk or tt.get("wijk") == wijk)
    ]
    taaktypes = {
        tt.get("taaktype"): tt.get("titel") for tt in taaktype_aantallen_per_melding
    }
    taaktype_aantallen = [
        {
            "taaktype": tt,
            "label": titel,
            "meer_dan_1": sum(
                [
                    d.get("melding_aantal")
                    for d in taaktype_aantallen_per_melding
                    for a in range(0, d.get("melding_aantal"))
                    if d.get("taaktype") == tt and d.get("aantal_per_melding") > 1
                ]
            ),
            "alles": sum(
                [
                    d.get("melding_aantal")
                    for d in taaktype_aantallen_per_melding
                    for a in range(0, d.get("melding_aantal"))
                    if d.get("taaktype") == tt
                ]
            ),
        }
        for tt, titel in taaktypes.items()
    ]

    taaktype_aantallen = sorted(
        [
            {
                "label": tt.get("label"),
                # "aantal": tt.get("meer_dan_1"),
                "percentage": round(float(tt.get("meer_dan_1") / tt.get("alles")) * 100)
                if tt.get("alles")
                else 0,
                "bar": round(float(tt.get("meer_dan_1") / tt.get("alles")) * 100)
                if tt.get("alles")
                else 0,
            }
            for tt in taaktype_aantallen
        ],
        key=lambda b: b.get("percentage"),
        reverse=True,
    )

    return {
        "title": "Meer dan 1 taaktype per melding",
        "head": ["Taaktype", "percentage"],
        "head_percentages": [80, 20],
        "body": taaktype_aantallen[:aantal] if aantal else taaktype_aantallen,
    }


def get_taaktype_aantallen_per_melding_tabs(
    taaktype_aantallen_per_melding, ticks=[], onderwerp=None, wijk=None
):
    labels = [t.get("label") for t in ticks]

    # print(json.dumps(taaktype_aantallen_per_melding[2], indent=4))

    alle_wijken = [wijk.get("wijknaam") for wijk in PDOK_WIJKEN]
    wijken = [wijk.get("wijknaam") for wijk in PDOK_WIJKEN]
    wijken_noord = [
        wijk.get("wijknaam") for wijk in PDOK_WIJKEN if wijk.get("stadsdeel") == "Noord"
    ]
    wijken_zuid = [
        wijk.get("wijknaam") for wijk in PDOK_WIJKEN if wijk.get("stadsdeel") == "Zuid"
    ]
    maximum_taaktype_aantal_over_tijdsvakken = sorted(
        [
            taaktype.get("aantal_per_melding")
            for tijdsvak in taaktype_aantallen_per_melding
            for taaktype in tijdsvak
        ],
        reverse=True,
    )
    maximum_taaktype_aantal_over_tijdsvakken = (
        maximum_taaktype_aantal_over_tijdsvakken[0] + 1
        if maximum_taaktype_aantal_over_tijdsvakken
        else 1
    )

    def get_kleur(i, max):
        if i == 1:
            return "#00811f"
        hr = 7
        h = i - 2
        max = max - 2
        step = h / (max - 1) if max > 1 else 0
        ll = hr * step
        h = round(hr - ll)
        h = hex(h)
        h = h.split("x")[1]
        h = h.rstrip("L")
        k = f"#ff{h}{h}00"
        return k

    datasets = [
        {
            "bron": taaktype_aantallen_per_melding,
            "aantal": i,
            "backgroundColor": get_kleur(i, maximum_taaktype_aantal_over_tijdsvakken),
        }
        for i in range(1, maximum_taaktype_aantal_over_tijdsvakken)
    ]
    tabs = (
        [
            {
                "wijken": [],
                "wijk_not_in": True,
                "titel": "Heel Rotterdam",
            },
            {
                "wijken": wijken_noord,
                "wijk_not_in": False,
                "titel": "Rotterdam noord",
            },
            {
                "wijken": wijken_zuid,
                "wijk_not_in": False,
                "titel": "Rotterdam zuid",
            },
            {
                "wijken": wijken,
                "wijk_not_in": True,
                "titel": "Onbekend of buiten Rotterdam",
            },
        ]
        if not wijk
        else [
            {
                "wijken": [w for w in alle_wijken if wijk == w],
                "wijk_not_in": False,
                "titel": wijk,
            }
        ]
    )

    def tab_aantal(tab):
        temp = [
            {
                "meer_dan_1": sum(
                    [
                        d.get("melding_aantal")  # * d.get("aantal_per_melding")
                        for d in tijdsvak
                        if d.get("aantal_per_melding") > 1
                        and bool(d.get("wijk") in tab.get("wijken"))
                        != bool(tab.get("wijk_not_in"))
                        and (not onderwerp or onderwerp == d.get("onderwerp"))
                    ]
                ),
                "alles": sum(
                    [
                        d.get("melding_aantal")  # * d.get("aantal_per_melding")
                        for d in tijdsvak
                        if bool(d.get("wijk") in tab.get("wijken"))
                        != bool(tab.get("wijk_not_in"))
                        and (not onderwerp or onderwerp == d.get("onderwerp"))
                    ]
                ),
            }
            for tijdsvak in taaktype_aantallen_per_melding
        ]
        totalen = [
            (t.get("meer_dan_1") / t.get("alles") * 100)
            for t in temp
            for i in range(0, t.get("alles"))
        ]
        return round(average(totalen))

    def tijdsvak_data(tijdsvak, dataset, tab):
        totaal_melding_aantallen = sum(
            [
                d.get("melding_aantal") * dataset.get("aantal")
                for d in tijdsvak
                if bool(d.get("wijk") in tab.get("wijken"))
                != bool(tab.get("wijk_not_in"))
                and (not onderwerp or onderwerp == d.get("onderwerp"))
            ]
        )
        melding_aantallen = sum(
            [
                d.get("melding_aantal") * dataset.get("aantal")
                for d in tijdsvak
                if d.get("aantal_per_melding") == dataset.get("aantal")
                and bool(d.get("wijk") in tab.get("wijken"))
                != bool(tab.get("wijk_not_in"))
                and (not onderwerp or onderwerp == d.get("onderwerp"))
            ]
        )
        return (
            round((melding_aantallen / totaal_melding_aantallen) * 100, 3)
            if totaal_melding_aantallen
            else 0
        )

    def tijdsvak_label(dataset):
        return f'Aantal {dataset.get("aantal")}'

    tabs = [
        {
            "titel": tab.get("titel"),
            "labels": labels,
            "aantal": tab_aantal(tab),
            "datasets": [
                {
                    "type": "bar",
                    "label": tijdsvak_label(dataset),
                    "borderColor": "#ffffff",
                    "fill": True,
                    "barPercentage": "0.5",
                    "backgroundColor": dataset.get("backgroundColor"),
                    "aantal": dataset.get("aantal"),
                    "data": [
                        tijdsvak_data(tijdsvak, dataset, tab)
                        for tijdsvak in dataset.get("bron")
                    ],
                }
                for dataset in datasets
            ],
        }
        for tab in tabs
    ]
    # remove datasets without relevant data
    tabs = [
        {
            **tab,
            "datasets": [
                dataset
                for dataset in tab.get("datasets", [])
                if sum(dataset.get("data"))
            ],
        }
        for tab in tabs
    ]
    return tabs


def get_nieuwe_taakopdrachten_tabs(
    nieuwe_taakopdrachten, ticks=[], onderwerp=None, wijk=None
):
    pass

    # print(json.dumps(nieuwe_taakopdrachten, indent=4))
    labels = [t.get("label") for t in ticks]

    alle_wijken = [wijk.get("wijknaam") for wijk in PDOK_WIJKEN]
    wijken = [wijk.get("wijknaam") for wijk in PDOK_WIJKEN]
    wijken_noord = [
        wijk.get("wijknaam") for wijk in PDOK_WIJKEN if wijk.get("stadsdeel") == "Noord"
    ]
    wijken_zuid = [
        wijk.get("wijknaam") for wijk in PDOK_WIJKEN if wijk.get("stadsdeel") == "Zuid"
    ]
    tabs = (
        [
            {
                "wijken": [],
                "wijk_not_in": True,
                "titel": "Heel Rotterdam",
            },
            {
                "wijken": wijken_noord,
                "wijk_not_in": False,
                "titel": "Rotterdam noord",
            },
            {
                "wijken": wijken_zuid,
                "wijk_not_in": False,
                "titel": "Rotterdam zuid",
            },
            {
                "wijken": wijken,
                "wijk_not_in": True,
                "titel": "Onbekend of buiten Rotterdam",
            },
        ]
        if not wijk
        else [
            {
                "wijken": [w for w in alle_wijken if wijk == w],
                "wijk_not_in": False,
                "titel": wijk,
            }
        ]
    )

    tabs = [
        {
            **tab,
            **{
                "datasets": [
                    {
                        "type": "line",
                        "label": "Aantal taken",
                        "bron": nieuwe_taakopdrachten,
                    },
                ]
            },
        }
        for tab in tabs
    ]

    tabs = [
        {
            "titel": tab.get("titel"),
            "labels": labels,
            "datasets": [
                {
                    "type": dataset.get("type"),
                    "label": dataset.get("label"),
                    "barPercentage": "0.5",
                    "borderColor": "#00811F",
                    "fill": True,
                    "backgroundColor": "rgba(0,200,100,0.1)",
                    "data": [
                        sum(
                            [
                                d.get("taakopdracht_aantal")
                                for d in dag
                                if bool(d.get("wijk") in tab.get("wijken"))
                                != bool(tab.get("wijk_not_in"))
                                and (not onderwerp or onderwerp == d.get("onderwerp"))
                            ]
                        )
                        for dag in dataset.get("bron")
                    ],
                }
                for dataset in tab.get("datasets", [])
            ],
        }
        for tab in tabs
    ]
    tabs = [
        {
            **tab,
            **{
                "aantal": sum(
                    [
                        sum(dataset.get("data", []))
                        for dataset in tab.get("datasets", [])
                    ]
                )
            },
        }
        for tab in tabs
    ]
    return tabs


def get_taken_nieuw_vs_afgehandeld_tabs(
    nieuwe_taakopdrachten, afgehandeld, ticks=[], onderwerp=None, wijk=None
):
    labels = [t.get("label") for t in ticks]

    alle_wijken = [wijk.get("wijknaam") for wijk in PDOK_WIJKEN]
    wijken = [wijk.get("wijknaam") for wijk in PDOK_WIJKEN]
    wijken_noord = [
        wijk.get("wijknaam") for wijk in PDOK_WIJKEN if wijk.get("stadsdeel") == "Noord"
    ]
    wijken_zuid = [
        wijk.get("wijknaam") for wijk in PDOK_WIJKEN if wijk.get("stadsdeel") == "Zuid"
    ]
    tabs = (
        [
            {
                "wijken": [],
                "wijk_not_in": True,
                "titel": "Heel Rotterdam",
            },
            {
                "wijken": wijken_noord,
                "wijk_not_in": False,
                "titel": "Rotterdam noord",
            },
            {
                "wijken": wijken_zuid,
                "wijk_not_in": False,
                "titel": "Rotterdam zuid",
            },
            {
                "wijken": wijken,
                "wijk_not_in": True,
                "titel": "Onbekend of buiten Rotterdam",
            },
        ]
        if not wijk
        else [
            {
                "wijken": [w for w in alle_wijken if wijk == w],
                "wijk_not_in": False,
                "titel": wijk,
            }
        ]
    )

    def afgehandeld_in_tijdsvak(t, tab):
        afgehandeld_data = [
            d.get("taakopdracht_aantal")
            for d in afgehandeld[t]
            if bool(d.get("wijk") in tab.get("wijken")) != bool(tab.get("wijk_not_in"))
            and (not onderwerp or onderwerp == d.get("onderwerp"))
        ]
        return sum(afgehandeld_data)

    def nieuw_in_tijdsvak(t, tab):
        meldingen_data = [
            d.get("taakopdracht_aantal")
            for d in nieuwe_taakopdrachten[t]
            if bool(d.get("wijk") in tab.get("wijken")) != bool(tab.get("wijk_not_in"))
            and (not onderwerp or onderwerp == d.get("onderwerp"))
        ]
        return sum(meldingen_data)

    tabs = [
        {
            **tab,
            **{
                "labels": labels,
                "datasets": [
                    {
                        "type": "line",
                        "label": "Aantal meldingen",
                        "borderColor": "#00811F",
                        "backgroundColor": "rgba(0,200,100,0.1)",
                        "fill": {
                            "target": "origin",
                            "below": "rgba(200, 0, 0, .1)",
                            "above": "rgba(0,200,100,0.1)",
                        },
                        "data": [
                            afgehandeld_in_tijdsvak(t, tab) - nieuw_in_tijdsvak(t, tab)
                            for t in range(0, len(labels))
                        ],
                    },
                ],
            },
        }
        for tab in tabs
    ]

    # print(json.dumps(tabs, indent=4))
    tabs = [
        {
            **tab,
            **{
                "aantal": sum(
                    [
                        sum([d for d in dataset.get("data", [])])
                        for dataset in tab.get("datasets", [])
                    ]
                )
            },
        }
        for tab in tabs
    ]
    return tabs
