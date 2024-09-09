import logging
import statistics

from apps.main.constanten import PDOK_WIJKEN

logger = logging.getLogger(__name__)


def average(lst):
    try:
        return statistics.mean(lst)
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

    def tijdsvak_status_gemiddelden(dag, statussen, tab, dag_index):
        status_gemiddelden = [
            float(d.get(status))
            for status in statussen
            for d in dag
            if bool(d.get("wijk") in tab.get("wijken")) != bool(tab.get("wijk_not_in"))
            and (not onderwerp or onderwerp == d.get("onderwerp"))
            and d.get(status) is not None
        ]
        gemiddeld = average(status_gemiddelden)
        return gemiddeld

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

    # print(json.dumps(tabs[0]["datasets"][0].get("data"), indent=4))

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


def top_vijf_aantal_meldingen_wijk(meldingen, valide_wijken, onderwerp=None):
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
        key=lambda b: b.get("percentage"),
        reverse=True,
    )
    aantal_meldingen_wijk = {
        "title": "Wijken met de meeste meldingen",
        "head": ["Wijk", "Aantal", "%"],
        "head_percentages": [65, 20, 15],
        "body": wijken,
    }
    return aantal_meldingen_wijk


def top_vijf_aantal_meldingen_onderwerp(meldingen, valide_onderwerpen, wijk=None):
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
        key=lambda b: b.get("percentage"),
        reverse=True,
    )
    aantal_meldingen_onderwerp = {
        "title": "Meest gemelde onderwerpen",
        "head": ["Onderwerp", "Aantal", "%"],
        "head_percentages": [65, 20, 15],
        "body": onderwerpen,
    }
    return aantal_meldingen_onderwerp


def top_vijf_aantal_onderwerpen_ontdubbeld(
    meldingen, signalen, valide_onderwerpen, wijk=None
):
    pass

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
        "body": onderwerpen_ontdubbeld,
    }
    return aantal_onderwerpen_ontdubbeld
