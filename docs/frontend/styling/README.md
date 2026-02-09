# Styling (SCSS) — PlanR

Dit document beschrijft hoe styling binnen PlanR is georganiseerd en hoe deze in de praktijk wordt gebruikt.
Het beschrijft uitsluitend de visuele laag (SCSS en themaconfiguratie).

Voor JavaScript-gedrag en interactie wordt verwezen naar:

- docs/frontend/controllers/README.md
- docs/frontend/patterns/README.md

Voor de globale context zie:

- docs/frontend/README.md

---

## Structuur

SCSS staat onder:

    app/frontend/assets/styles/

Belangrijkste bestanden:

- app.scss
- _theme.scss
- _base.scss
- _print.scss
- components/

---

## Entry en bundling

Webpack heeft één entry (`app.js`).

Vanuit JavaScript wordt SCSS geïmporteerd, meestal via `app.scss`.

Alle styling komt uiteindelijk in één hoofd-bundle terecht.

---

## Build output en caching

Assets worden gebouwd naar:

    public/build/

Bestanden krijgen hashes:

- app-[hash].js
- app-[hash].css

Hierdoor worden caches bij nieuwe builds automatisch omzeild.

In development wordt hashing voor JS uitgeschakeld.

---

## Thema en variabelen

Globale variabelen staan in `_theme.scss`.

Hierin staan onder andere:

- kleurpalet
- Bootstrap-achtige theme colors
- breakpoints
- container-instellingen
- form- en modalvariabelen
- typografie

Veel component-styling is hier indirect van afhankelijk.

---

## Breakpoints

Breakpoints zijn gedefinieerd als:

- sm: 576px
- md: 768px
- lg: 1024px
- xl: 1280px
- xxl: 1440px

Ze worden gebruikt via `map-get($grid-breakpoints, ...)`.

De codebase is grotendeels mobile-first, met enkele uitzonderingen.

---

## Component partials

Onder `components/` staan stylingbestanden per component of view.

Er is geen strikt onderscheid tussen “component” en “pagina”.

Veel bestanden bevatten een mix van beide.

Voorbeelden:

- dashboard
- incident-details
- navigation
- forms
- messages

---

## Importstructuur

De meeste partials worden via app.scss geïmporteerd.

De exacte volgorde is historisch gegroeid.

Nieuwe bestanden moeten handmatig aan de importlijst worden toegevoegd.

---

## Print styling

_print.scss bevat print-specifieke regels.

Deze worden via imports meegenomen in de hoofd-bundle.

Er is geen aparte print-bundle.

---

## Assets

Icons, images en fonts worden via CopyWebpackPlugin gekopieerd.

Deze bestanden hebben geen hashing in de naam.

Caching hiervan is afhankelijk van infrastructuur.

---

## Ontwikkelpraktijk

Styling wordt meestal aangepast in bestaande partials.

Nieuwe partials worden vooral toegevoegd bij grotere nieuwe views.

Refactors van oude styling zijn beperkt uitgevoerd.
