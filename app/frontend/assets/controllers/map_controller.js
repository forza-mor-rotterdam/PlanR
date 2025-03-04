import { Controller } from '@hotwired/stimulus'
import L from 'leaflet'

export default class extends Controller {
  static targets = ['tiles', 'pin', 'details']
  static values = {
    defaultLatLon: String,
  }

  init() {
    this.markerList = []
    this.coordinates = []
    const url =
      'https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0/{layerName}/{crs}/{z}/{x}/{y}.{format}'
    const config = {
      crs: 'EPSG:3857',
      format: 'png',
      name: 'standaard',
      layerName: 'standaard',
      type: 'wmts',
      minZoom: 11,
      maxZoom: 19,
      tileSize: 256,
      attribution: '',
    }
    this.map = L.map(this.tilesTarget).setView(this.defaultLatLon, 18)

    L.tileLayer(url, config).addTo(this.map)

    this.map.on('popupopen popupclose', ({ popup }) => {
      if (popup instanceof L.Popup) {
        const marker = popup._source
        const eventName = popup.isOpen() ? 'markerSelectedEvent' : 'markerDeselectedEvent'
        const event = new CustomEvent(eventName, {
          bubbles: true,
          cancelable: false,
          detail: { options: marker.options },
        })
        console.log('POPUPevent', event)
        this.element.dispatchEvent(event)
      }
    })
  }
  tilesTargetConnected() {
    this.defaultLatLon = this.hasDefaultLatLonValue
      ? JSON.parse(this.defaultLatLonValue)
      : [51.92442, 4.47775]
    this.init()
  }

  toggleDetails(event) {
    if (!event.target.open) return
    this.detailsTargets.forEach((details) => {
      if (details !== event.target) {
        details.open = false
      }
    })
  }

  fitMarkers() {
    const bounds = new L.LatLngBounds(this.coordinates)
    this.map.fitBounds(bounds, { padding: [50, 50] })
  }
  pinTargetConnected(pin) {
    console.log(pin)
    const latLon = JSON.parse(pin.dataset.latLon)
    if (latLon && pin.dataset.pinId) {
      this.coordinates.push(latLon)
      const marker = new L.Marker(latLon, {
        icon: this.markerMagenta(),
        markerId: pin.dataset.pinId,
      })
      marker.addTo(this.map)
      this.markerList.push(marker)
      if (pin.dataset.popupContent) {
        marker.bindPopup(pin.dataset.popupContent)
      }
      const details = pin.closest('details')
      if (details) {
        details.addEventListener('toggle', () => {
          marker.setIcon(details.hasAttribute('open') ? this.markerGreen() : this.markerMagenta())
        })
        pin.addEventListener('click', () => {
          console.lof('pin click, details: ', details)
          details.open = true
        })
      }
      this.fitMarkers()
    }
  }

  markerIcon() {
    return L.Icon.extend({
      options: {
        iconSize: [32, 32],
        iconAnchor: [18, 18],
        popupAnchor: [0, -17],
      },
    })
  }
  markerMagenta() {
    const iconClass = this.markerIcon()
    return new iconClass({
      iconUrl:
        'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBjbGlwLXJ1bGU9ImV2ZW5vZGQiIGQ9Ik0yMy43NzgzIDYuMjI0MTJDMTkuNTAwMyAxLjk0NjEzIDEyLjQ5OTkgMS45NDYxMyA4LjIyMTkzIDYuMjI0MTJDMy45NDM5MyAxMC41MDIxIDMuOTQzOTMgMTcuNTAyNSA4LjIyMTkzIDIxLjc4MDVMMTYuMDAwMSAyOS41NTg2TDIzLjc3ODMgMjEuNzgwNUMyOC4wNTYzIDE3LjUwMjUgMjguMDU2MyAxMC41MDIxIDIzLjc3ODMgNi4yMjQxMlpNMTYuMDAwMSAxOC4wMDIzQzE4LjIwOTIgMTguMDAyMyAyMC4wMDAxIDE2LjIxMTQgMjAuMDAwMSAxNC4wMDIzQzIwLjAwMDEgMTEuNzkzMiAxOC4yMDkyIDEwLjAwMjMgMTYuMDAwMSAxMC4wMDIzQzEzLjc5MSAxMC4wMDIzIDEyLjAwMDEgMTEuNzkzMiAxMi4wMDAxIDE0LjAwMjNDMTIuMDAwMSAxNi4yMTE0IDEzLjc5MSAxOC4wMDIzIDE2LjAwMDEgMTguMDAyM1oiIGZpbGw9IiNDOTM2NzUiLz4KPC9zdmc+Cg==',
    })
  }
  markerGreen() {
    const iconClass = this.markerIcon()
    return new iconClass({
      iconUrl:
        'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjYiIHZpZXdCb3g9IjAgMCAyMCAyNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICAgIDxwYXRoIGQ9Ik0xNy42MzQ4IDMuNjEzMTVDMTYuNzA4OSAyLjQ4Mzc1IDE1LjU0MzkgMS41NzM4OCAxNC4yMjM5IDAuOTQ5MTM4QzEyLjkwMzggMC4zMjQzOTEgMTEuNDYxNiAwLjAwMDMzNTY5MyAxMC4wMDEyIDAuMDAwMzM1NjkzQzguNTQwNzIgMC4wMDAzMzU2OTMgNy4wOTg0OSAwLjMyNDM5MSA1Ljc3ODQzIDAuOTQ5MTM4QzQuNDU4MzggMS41NzM4OCAzLjI5MzQgMi40ODM3NSAyLjM2NzQ4IDMuNjEzMTVDMC44Mzc1NTUgNS40Njg3MiAwLjAwMDg1NDQ5MiA3Ljc5ODc1IDAuMDAwODU0NDkyIDEwLjIwMzdDMC4wMDA4NTQ0OTIgMTIuNjA4NyAwLjgzNzU1NSAxNC45Mzg3IDIuMzY3NDggMTYuNzk0M0wxMC4wMDEyIDI2LjAwMDVMMTcuNjM2IDE2Ljc5NDNDMTkuMTY1MSAxNC45MzgzIDIwLjAwMTIgMTIuNjA4MyAyMC4wMDEgMTAuMjAzNUMyMC4wMDA4IDcuNzk4NzIgMTkuMTY0MyA1LjQ2ODg2IDE3LjYzNDggMy42MTMxNVpNMTAgMTMuOTk5MUM5LjExMDA0IDEzLjk5OTEgOC4yNDAwNCAxMy43MzUyIDcuNTAwMDUgMTMuMjQwN0M2Ljc2MDA2IDEyLjc0NjMgNi4xODMzMSAxMi4wNDM1IDUuODQyNzMgMTEuMjIxM0M1LjUwMjE1IDEwLjM5OSA1LjQxMzAzIDkuNDk0MjggNS41ODY2NiA4LjYyMTRDNS43NjAyOSA3Ljc0ODUyIDYuMTg4ODUgNi45NDY3MyA2LjgxODE3IDYuMzE3NDFDNy40NDc0OCA1LjY4ODEgOC4yNDkyNyA1LjI1OTU0IDkuMTIyMTUgNS4wODU5MUM5Ljk5NTAzIDQuOTEyMjggMTAuODk5OCA1LjAwMTM5IDExLjcyMiA1LjM0MTk4QzEyLjU0NDMgNS42ODI1NiAxMy4yNDcgNi4yNTkzMSAxMy43NDE1IDYuOTk5M0MxNC4yMzU5IDcuNzM5MjkgMTQuNDk5OCA4LjYwOTI5IDE0LjQ5OTggOS40OTkyN0MxNC40OTk4IDEwLjY5MjggMTQuMDI1OCAxMS44Mzc1IDEzLjE4MTkgMTIuNjgxNUMxMi4zMzgxIDEzLjUyNTYgMTEuMTkzNiAxMy45OTk5IDEwIDE0LjAwMDJWMTMuOTk5MVoiIGZpbGw9IiMwMDgxMUYiLz4KPC9zdmc+Cg==',
    })
  }
}
