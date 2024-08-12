import { Controller } from '@hotwired/stimulus'
import L from 'leaflet'

export default class extends Controller {
  static targets = ['map']
  connect() {
    console.log(this.mapTargets)
    if (this.hasMapTarget) {
      const url =
        'https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0/{layerName}/{crs}/{z}/{x}/{y}.{format}'
      const config = {
        crs: 'EPSG:3857',
        format: 'png',
        name: 'standaard',
        layerName: 'standaard',
        type: 'wmts',
        minZoom: 1,
        maxZoom: 19,
        tileSize: 256,
        opacity: 0,
        attribution: '',
      }
      this.map = L.map(this.mapTarget, {
        zoomControl: false,
        closePopupOnClick: false,
        boxZoom: false,
        doubleClickZoom: false,
        dragging: false,
        trackResize: false,
        keyboard: false,
        scrollWheelZoom: false,
      })
      L.tileLayer(url, config).addTo(this.map)

      const getStyle = (feature) => {
        switch (feature.properties.wk_naam) {
          case 'Delfshaven':
            return { color: 'green', opacity: 1, fillOpacity: 1 }
          default:
            return { color: '#88bb88', opacity: 1, fillOpacity: 1 }
        }
      }
      // eslint-disable-next-line no-undef
      this.rdamLayer = new L.geoJSON(rdam, {
        style: getStyle,
      }).addTo(this.map)
      this.map.fitBounds(this.rdamLayer.getBounds())
    }
  }
}
