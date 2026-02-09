# Patterns — PlanR

Dit document beschrijft terugkerende technische patronen die in de praktijk binnen PlanR zijn ontstaan.

Het vormt een aanvulling op:

- docs/frontend/README.md (context)
- docs/frontend/controllers/README.md (implementatie)
- docs/frontend/styling/README.md (presentatie)

De beschreven patronen zijn gebaseerd op bestaande code en gewoontes, niet op theoretische architectuurprincipes.

---

## HTML en Stimulus

De basis is:

- Django rendert HTML
- data-attributen configureren gedrag
- Stimulus koppelt logica

Dit patroon komt overal terug.

---

## Data-overdracht vanuit Django

Data wordt meestal aangeleverd via:

- data-*-value attributen
- JSON in attributes
- hidden inputs

Welke aanpak wordt gebruikt verschilt per pagina.

---

## State en communicatie

Er bestaat geen centrale state-store.

State zit meestal in:

- controller properties
- DOM
- Stimulus values

Controllers communiceren soms via custom events.

---

## Requests en backend-communicatie

request_controller.js wordt gebruikt voor fetch-aanroepen.

Andere controllers gebruiken soms eigen fetch-implementaties.

Er is geen volledig gecentraliseerde API-layer.

---

## Build en versie-informatie

Webpack injecteert:

    __GIT_SHA__

Deze waarde kan worden gebruikt voor debugging en versieherkenning.

Gebruik hiervan is beperkt en niet overal doorgevoerd.

---

## Overlay-systeem

Modals, sidesheets en infosheets worden verzorgd door:

- modal
- sidesheet
- infosheet
- overflow
- focus_trap

Deze controllers werken samen, maar vormen geen formeel framework.

Gedrag is deels impliciet.

---

## Tabellen

Tabellen worden opgebouwd met:

- table
- pagination
- sorter
- lazyload

De precieze combinatie verschilt per view.

---

## Charts

Charts worden geïmplementeerd via aparte controllers met helpers.

Configuratie en datavorm verschilt per dashboard.

---

## Performance

Performance-optimalisaties zijn meestal lokaal toegepast:

- debouncing
- lazy loading
- beperken van reflows

Er is geen centraal performance-framework.

---

## Ontwikkelpraktijk

Nieuwe patronen ontstaan meestal organisch.

Ze worden zelden formeel vastgelegd en verspreiden zich via copy/paste en voorbeeldcode.
