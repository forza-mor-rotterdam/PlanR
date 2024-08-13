import json
import statistics
from datetime import datetime, timedelta

from apps.main.constanten import DAGEN_VAN_DE_WEEK_KORT, MAANDEN_KORT, PDOK_WIJKEN


def get_aantallen_tabs(meldingen, signalen, week):
    maandag = datetime.strptime(f"{week.year}-{week.week}-1", "%Y-%W-%w").date()
    labels = []
    for weekdag in range(0, 7):
        dag = maandag + timedelta(days=weekdag)
        labels.append(
            f"{DAGEN_VAN_DE_WEEK_KORT[weekdag]} {dag.strftime('%-d')} {MAANDEN_KORT[dag.month-1]}"
        )

    wijken = [wijk.get("wijknaam") for wijk in PDOK_WIJKEN]
    wijken_noord = [
        wijk.get("wijknaam") for wijk in PDOK_WIJKEN if wijk.get("stadsdeel") == "Noord"
    ]
    wijken_zuid = [
        wijk.get("wijknaam") for wijk in PDOK_WIJKEN if wijk.get("stadsdeel") == "Zuid"
    ]

    tabs = [
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
                    "barPercentage": "0.2",
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


def get_status_veranderingen_tabs(veranderingen, week):
    maandag = datetime.strptime(f"{week.year}-{week.week}-1", "%Y-%W-%w").date()
    labels = []
    for weekdag in range(0, 7):
        dag = maandag + timedelta(days=weekdag)
        labels.append(
            f"{DAGEN_VAN_DE_WEEK_KORT[weekdag]} {dag.strftime('%-d')} {MAANDEN_KORT[dag.month-1]}"
        )

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

    print(veranderingen)
    tabs = [
        {
            **tab,
            **{
                "datasets": [
                    {
                        "type": "line",
                        "label": "gemiddelde duur (seconden)",
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
                        statistics.mean(
                            [
                                float(d.get("duur_seconden_gemiddeld"))
                                for d in dag
                                if d.get("begin_status") == tab.get("begin_status")
                                and d.get("eind_status") == tab.get("eind_status")
                            ]
                        )
                        if [
                            d.get("duur_seconden_gemiddeld")
                            for d in dag
                            if d.get("begin_status") == tab.get("begin_status")
                            and d.get("eind_status") == tab.get("eind_status")
                        ]
                        else 0
                        for dag in dataset.get("bron")
                    ],
                }
                for dataset in tab.get("datasets", [])
            ],
        }
        for tab in tabs
    ]
    print(json.dumps(tabs, indent=4))
    tabs = [
        {
            **tab,
            **{
                "aantallen": [
                    int(statistics.mean(dataset.get("data", [])))
                    if dataset.get("data", [])
                    else 0
                    for dataset in tab.get("datasets", [])
                ]
            },
        }
        for tab in tabs
    ]
    return tabs
