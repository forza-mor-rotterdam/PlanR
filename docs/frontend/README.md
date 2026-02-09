# Front-End Documentatie — PlanR

Deze documentatie beschrijft hoe de front-end van PlanR in de praktijk is opgebouwd en hoe deze in de loop van de tijd is gegroeid.

De documentatie is bedoeld voor overdracht aan een opvolgende front-end developer en richt zich op begrip van de bestaande code, niet op het opleggen van nieuwe architectuurprincipes.

De front-end documentatie bestaat uit vier onderdelen:

- docs/frontend/README.md (dit document)
- docs/frontend/controllers/README.md
- docs/frontend/styling/README.md
- docs/frontend/patterns/README.md

---

## Doel van deze documentatie

Deze documentatie heeft als doel:

- inzicht geven in hoe de front-end technisch in elkaar zit
- uitleggen waar logica en styling te vinden zijn
- context geven bij historische keuzes
- voorkomen dat kennis alleen “in hoofden” zit

Het is geen handleiding voor beginners en geen theoretisch architectuurdocument.

---

## Globale architectuur

PlanR is een Django-applicatie met server-side rendering.

De basisopzet is:

- Django rendert HTML via templates
- In templates worden data-attributen toegevoegd
- JavaScript verrijkt deze pagina’s via Stimulus
- Styling wordt geleverd via SCSS-bundles
- Webpack verzorgt bundling en cache busting

De applicatie is geen SPA. Navigatie en rendering gebeuren grotendeels server-side, met client-side interactie waar nodig.

---

## Front-end broncode

Alle front-end assets staan onder:

    app/frontend/assets/

Belangrijkste onderdelen:

- app.js en bootstrap.js (startpunt)
- controllers/ (Stimulus controllers)
- styles/ (SCSS)
- images/, icons/, json/
- script/ (losse scripts)

Deze map bevat vrijwel alle front-end logica en styling.

---

## Ontwikkelen en bouwen

De front-end wordt gebouwd met npm en Webpack.

In de praktijk worden meestal de volgende commando’s gebruikt:

    npm install
    npm run watch
    npm run build

De exacte scripts staan in package.json en in de root README.

Tijdens ontwikkeling wordt vaak gewerkt met een watcher en een Django-devserver.

---

## Build en integratie met Django

Webpack bouwt de front-end bundles en schrijft deze naar:

    public/build/

Via webpack-bundle-tracker wordt een `webpack-stats.json` gegenereerd, die door Django wordt gebruikt om de juiste assets in templates te laden.

Hierdoor hoeven bestandsnamen met hashes niet handmatig te worden aangepast.

---

## Indeling van de documentatie

De front-end documentatie is opgesplitst in vier delen die samen gelezen moeten worden:

- Dit document beschrijft de globale opzet en context
- controllers/README.md beschrijft waar de JavaScript-logica zit
- styling/README.md beschrijft hoe de visuele laag is opgebouwd
- patterns/README.md beschrijft terugkerende technische oplossingen

Geen van deze documenten is op zichzelf volledig; ze vullen elkaar aan.

---

## Historische context

De front-end van PlanR is in meerdere fases gegroeid.

Gevolgen hiervan zijn onder andere:

- verschillen in stijl tussen controllers
- overlap tussen component- en paginastyling
- verschillende oplossingsrichtingen naast elkaar
