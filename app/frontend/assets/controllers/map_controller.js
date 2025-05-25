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
    const latLon = JSON.parse(pin.dataset.latLon)
    if (latLon && pin.dataset.pinId) {
      this.coordinates.push(latLon)
      const marker = new L.Marker(latLon, {
        icon: this.lichtmastgrijs(),
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
          marker.setIcon(
            details.hasAttribute('open') ? this.lichtmastgroen() : this.lichtmastgrijs()
          )
        })
        marker.on('click', () => {
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
  lichtmastgroen() {
    const iconClass = this.markerIcon()
    return new iconClass({
      iconUrl:
        'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTgiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCAxOCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTguNjc5NjkgMC40OTIxODhDMTMuMTc1NyAwLjQ5MjE4OCAxNi43OTg2IDQuMDM4OTUgMTYuNzk4OCA4LjM4NjcyQzE2Ljc5ODggMTIuNzM0NyAxMy4xNzU5IDE2LjI4MjIgOC42Nzk2OSAxNi4yODIyQzQuMTgzNjYgMTYuMjgyMSAwLjU2MTUyMyAxMi43MzQ2IDAuNTYxNTIzIDguMzg2NzJDMC41NjE3ODkgNC4wMzkwNSA0LjE4MzgyIDAuNDkyMzU4IDguNjc5NjkgMC40OTIxODhaIiBmaWxsPSIjMDA4MTFGIiBzdHJva2U9IiMwMDgxMUYiLz4KPHBhdGggZD0iTTguNjc5NjkgNS43MzQzOEMxMC4yMDEgNS43MzQzOCAxMS40MTIxIDYuOTMyNTkgMTEuNDEyMSA4LjM4MjgxQzExLjQxMTkgOS44MzI4OSAxMC4yMDA4IDExLjAzMDMgOC42Nzk2OSAxMS4wMzAzQzcuMTU4NzYgMTEuMDMgNS45NDg0MSA5LjgzMjc0IDUuOTQ4MjQgOC4zODI4MUM1Ljk0ODI0IDYuOTMyNzUgNy4xNTg2NSA1LjczNDYzIDguNjc5NjkgNS43MzQzOFoiIGZpbGw9IndoaXRlIiBzdHJva2U9IiMwMDgxMUYiLz4KPGxpbmUgeDE9IjguNDE0MDYiIHkxPSIxNC4yNzM0IiB4Mj0iOC40MTQwNiIgeTI9IjM5LjIwODQiIHN0cm9rZT0iIzAwODExRiIgc3Ryb2tlLXdpZHRoPSIyIi8+Cjwvc3ZnPgo=',
    })
  }
  lichtmastgrijs() {
    const iconClass = this.markerIcon()
    return new iconClass({
      iconUrl:
        'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMTgiIGhlaWdodD0iNDAiIHZpZXdCb3g9IjAgMCAxOCA0MCIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZD0iTTguODI0MjIgMC44NDM3NUMxMy4zMjAyIDAuODQzNzUgMTYuOTQzMSA0LjM5MDUxIDE2Ljk0MzQgOC43MzgyOEMxNi45NDM0IDEzLjA4NjMgMTMuMzIwNCAxNi42MzM4IDguODI0MjIgMTYuNjMzOEM0LjMyODE5IDE2LjYzMzYgMC43MDYwNTUgMTMuMDg2MiAwLjcwNjA1NSA4LjczODI4QzAuNzA2MzIgNC4zOTA2MSA0LjMyODM1IDAuODQzOTIgOC44MjQyMiAwLjg0Mzc1WiIgZmlsbD0iIzY2NjY2NiIgc3Ryb2tlPSIjNjY2NjY2Ii8+CjxwYXRoIGQ9Ik04LjgyNDIyIDYuMDg1OTRDMTAuMzQ1NSA2LjA4NTk0IDExLjU1NjYgNy4yODQxNiAxMS41NTY2IDguNzM0MzhDMTEuNTU2NSAxMC4xODQ1IDEwLjM0NTQgMTEuMzgxOCA4LjgyNDIyIDExLjM4MThDNy4zMDMyOSAxMS4zODE2IDYuMDkyOTUgMTAuMTg0MyA2LjA5Mjc3IDguNzM0MzhDNi4wOTI3NyA3LjI4NDMxIDcuMzAzMTggNi4wODYxOSA4LjgyNDIyIDYuMDg1OTRaIiBmaWxsPSJ3aGl0ZSIgc3Ryb2tlPSIjNjY2NjY2Ii8+CjxsaW5lIHgxPSI4LjU1OTU3IiB5MT0iMTQuNjI1IiB4Mj0iOC41NTk1NyIgeTI9IjM5LjU2IiBzdHJva2U9IiM2NjY2NjYiIHN0cm9rZS13aWR0aD0iMiIvPgo8L3N2Zz4K',
    })
  }
}
