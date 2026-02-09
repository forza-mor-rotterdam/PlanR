# Stimulus Controllers — PlanR

Dit document vormt samen met:

- docs/frontend/README.md
- docs/frontend/styling/README.md
- docs/frontend/patterns/README.md

een samenhangend overzicht van de front-end van PlanR.

Waar dit document focust op JavaScript-gedrag, beschrijven de andere documenten respectievelijk de globale architectuur, styling en herbruikbare patronen.

Dit document beschrijft hoe Stimulus controllers binnen PlanR worden gebruikt en hoe deze in de praktijk zijn opgebouwd.

Voor algemene informatie over Stimulus:
https://stimulus.hotwired.dev

---

## Rol van controllers in PlanR

In PlanR vormen Stimulus controllers de belangrijkste client-side laag.

Controllers worden gebruikt voor:

- afhandelen van gebruikersinteractie
- formulierlogica
- openen en sluiten van overlays
- tabellen, filters en dashboards
- synchronisatie met backend endpoints
- notificaties

Vrijwel alle dynamiek in de interface loopt via controllers.

---

## Locatie en structuur

Controllers staan onder:

    app/frontend/assets/controllers/

Er bestaan enkele submappen voor specifieke domeinen:

- beheer/
- notificaties/
- table/
- taken_aanmaken/

De meeste controllers staan echter direct in de root van deze map.

De indeling is historisch gegroeid en niet overal strikt doorgevoerd.

---

## Registratie en bootstrap

De initialisatie van Stimulus gebeurt via:

- app.js
- bootstrap.js
- controllers.json

`controllers.json` fungeert als manifest van beschikbare controllers.

Tijdens het opstarten van de front-end worden deze controllers geregistreerd en gekoppeld aan hun identifiers.

Nieuwe controllers moeten in de praktijk zowel als bestand bestaan als in de bootstrap/manifest opgenomen zijn.

---

## Omvang en verantwoordelijkheden

Controllers verschillen sterk in omvang.

Er zijn:

- kleine controllers met één taak
- middelgrote controllers voor componenten
- grotere controllers die meerdere verantwoordelijkheden combineren

Met name domeincontrollers (dashboard, detail, formulieren) zijn soms vrij groot.

Dit is grotendeels historisch gegroeid.

---

## Overzicht van controllers

### Core en navigatie

- main_controller.js
- head_controller.js
- navigation_controller.js
- topbar_controller.js
- sessionTimer_controller.js

Deze controllers verzorgen de globale shell van de applicatie.

---

### Overzicht, detail en dashboards

- overview_controller.js
- detail_controller.js
- dashboard_controller.js
- dashboardMap_controller.js

Formulieren en flows:

- meldingbehandelformulier_controller.js
- melding_afhandelreden_controller.js
- melding_pauzeren_controller.js
- melding_heropenen_controller.js
- externeomschrijvingformulier_controller.js
- locatieaanpassenformulier_controller.js
- opmerkingformulier_controller.js
- meldingGebruiker_controller.js

---

### Filtering en requests

- filter_controller.js
- row_search_controller.js
- request_controller.js

Deze controllers verzorgen filtering, zoeken en communicatie met de backend.

---

### Tabellen

- table_controller.js
- table-paginated_controller.js
- sorter_controller.js

Deze vormen samen het tabellen-subsystem.

---

### Media en viewers

- bijlagen_controller.js
- image_slider_controller.js
- modal_image_slider_controller.js
- hero-image_controller.js

---

### Overlays en layout

- modal_controller.js
- sidesheet_controller.js
- infosheet_controller.js
- overflow_controller.js
- overflow_toggle_controller.js
- focus_trap_controller.js

Deze controllers werken samen voor modals, sidesheets en focus/scroll management.

---

### Notificaties en berichten

- berichten_beheer_controller.js
- messages_controller.js

Notificaties:

- manager_controller.js
- toast_item_controller.js
- snack_item_controller.js
- snack_overzicht_item_controller.js
- toast_manager_controller.js

---

### Input helpers

- selectAll_controller.js
- datetime_controller.js
- characterCount_controller.js
- input_char_counter_controller.js
- dagen_uren_controller.js

---

### Charts en visualisaties

- chart_bar_controller.js
- chart_doughnut_controller.js
- chart_line_controller.js
- chart_slider_controller.js
- chart_helper_controller.js
- chart_utils_controller.js

---

### Exports en utilities

- csv_download_controller.js
- utils_controller.js
- subSelect_controller.js
- radio_select_compact_controller.js
- radioSelectPaginator_controller.js
- select2Modal_controller.js
- lazyload-table-bar_controller.js
- map_controller.js

---

## Debuggen en testen

Controllers worden meestal getest op bestaande pagina’s.

Gebruikelijk is:

- logging in connect()
- inspectie van data-attributen
- werken via browser DevTools

Er bestaat geen aparte testomgeving voor individuele controllers.

---

## Ontwikkelpraktijk

In de praktijk worden controllers meestal aangepast binnen hun bestaande context.

Grotere refactors zijn zeldzaam en worden alleen uitgevoerd als dat functioneel nodig is.
