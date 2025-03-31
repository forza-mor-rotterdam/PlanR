import { Controller } from '@hotwired/stimulus'
import { visit } from '@hotwired/turbo'
import L from 'leaflet'

let detailScrollY = 0,
  distance = 0,
  actionsHeight = 0

export default class extends Controller {
  static values = {
    signalen: String,
    locaties: String,
    afbeeldingen: String,
    urlPrefix: String,
  }
  static targets = ['turboActionModal', 'btnToTop', 'containerActions', 'lichtmast']

  initialize() {
    this.coordinates = []
    if (this.hasTabsTarget && this.hasTabsContentTarget) {
      const tabs = this.tabsTarget.querySelectorAll('.btn--tab')
      const tabsContent = this.tabsContentTarget.querySelectorAll('.tab-content')
      this.activateTabs(tabs, tabsContent, this)
    }

    if (this.hasTabs2Target && this.hasTabsContent2Target) {
      const tabs = this.tabs2Target.querySelectorAll('.btn--tab')
      const tabsContent = this.tabsContent2Target.querySelectorAll('.tab-content')
      this.activateTabs(tabs, tabsContent, this)
    }
    const locaties = this.hasLocatiesValue ? JSON.parse(this.locatiesValue) : []
    const validLocaties = locaties
      .filter((locatie) => locatie.geometrie?.coordinates)
      .sort((a, b) => b.gewicht - a.gewicht)
    const locatiePrimair = validLocaties.find(
      (locatie) => locatie.geometrie?.coordinates && locatie.primair
    )
    const locatie = locatiePrimair ? locatiePrimair : validLocaties[0]
    const mapDiv = document.getElementById('incidentMap')
    this.mapLayers = {
      containers: {
        layer: L.tileLayer.wms(
          'https://www.gis.rotterdam.nl/GisWeb2/js/modules/kaart/WmsHandler.ashx',
          {
            layers: 'OBS.OO.CONTAINER',
            format: 'image/png',
            transparent: true,
            minZoom: 10,
            maxZoom: 19,
          }
        ),
        legend: [],
      },
      EGD: {
        layer: L.tileLayer.wms(
          'https://www.gis.rotterdam.nl/GisWeb2/js/modules/kaart/WmsHandler.ashx',
          {
            layers: 'BSB.OBJ.EGD',
            format: 'image/png',
            transparent: true,
            minZoom: 10,
            maxZoom: 19,
          }
        ),
      },
      lichtmasten: {
        layer: L.tileLayer.wms(
          'https://www.gis.rotterdam.nl/GisWeb2/js/modules/kaart/WmsHandler.ashx',
          {
            layers: 'OBSURV.OVL.LP',
            format: 'image/png',
            transparent: true,
            minZoom: 10,
            maxZoom: 19,
          }
        ),
      },
      lichtmastenSto: {
        layer: L.tileLayer.wms(
          'https://www.gis.rotterdam.nl/GisWeb2/js/modules/kaart/WmsHandler.ashx',
          {
            layers: 'OBSURV.OVL.LP.STO',
            format: 'image/png',
            transparent: true,
            minZoom: 10,
            maxZoom: 19,
          }
        ),
      },
    }

    if (mapDiv && locatie) {
      this.coordinates.push(locatie.geometrie.coordinates.reverse())
      const url =
        'https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0/{layerName}/{crs}/{z}/{x}/{y}.{format}'
      const config = {
        crs: 'EPSG:3857',
        format: 'png',
        name: 'standaard',
        layerName: 'standaard',
        type: 'wmts',
        minZoom: 12,
        maxZoom: 19,
        tileSize: 256,
        attribution: '',
      }
      this.map = L.map('incidentMap').setView(this.coordinates[0], 18)
      L.tileLayer(url, config).addTo(this.map)

      this.addSignalen()
      this.fitMarkers()
      new L.Marker(this.coordinates[0], { icon: this.markerGreen() }).addTo(this.map)
    }
  }

  connect() {
    document.documentElement.scrollTop = detailScrollY
    this.urlParams = new URLSearchParams(window.location.search)
    this.tabIndex = Number(this.urlParams.get('tabIndex'))
    this.selectTab(this.tabIndex || 1)
    actionsHeight = this.containerActionsTarget.offsetHeight
    this.ticking = false
    this.updatePosition = this.updatePosition.bind(this)
    window.addEventListener('scroll', () => {
      this.checkScrollPosition()
    })
  }
  fitMarkers() {
    const bounds = new L.LatLngBounds(this.coordinates)
    this.map.fitBounds(bounds)
  }
  lichtmastTargetConnected(lichtmast) {
    const lichtmastData = JSON.parse(lichtmast.dataset.lichtmastData)
    const gps = lichtmastData.find((d) => d[0] === 'gps')
    if (gps) {
      this.coordinates.push(gps[1])
      const marker = new L.Marker(gps[1], { icon: this.markerMagenta() })
      marker.addTo(this.map)
      const ldHTML = lichtmastData
        .filter((ld) => !['rd'].includes(ld[0]))
        .reduce((o, ld) => `${o}<dt>${ld[0]}</dt><dd>${ld[1] || '-'}</dd>`, '')
      const popupContent = `<div></div><div class="container__content"><dl>${ldHTML}</dl></div>`
      marker.bindPopup(popupContent)
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
  addSignalen() {
    if (this.signalenValue) {
      this.signalen =
        JSON.parse(this.signalenValue)?.filter(
          (signaal) =>
            signaal.locaties_voor_signaal
              .filter((locatie) => locatie.geometrie?.coordinates)
              .find((elem) => elem)?.geometrie?.coordinates
        ) ?? []
      for (const signaal of this.signalen) {
        const coordinates = signaal.locaties_voor_signaal
          .filter((locatie) => locatie.geometrie?.coordinates)[0]
          .geometrie.coordinates.reverse()
        this.coordinates.push(coordinates)
        const marker = new L.Marker(coordinates, { icon: this.markerMagenta() })
        marker.addTo(this.map)
        const popupContent = `<div></div><div class="container__content"><p>${signaal.bron_signaal_id}</p></div>`
        marker.bindPopup(popupContent)
      }
    }
  }
  checkScrollPosition() {
    if (window.innerWidth > 767) {
      if (distance === 0) {
        distance = this.containerActionsTarget.getBoundingClientRect().top
      }
      // scrolltotop
      if (document.body.scrollTop >= 100 || document.documentElement.scrollTop >= 100) {
        this.btnToTopTarget.classList.add('show')
      } else {
        this.btnToTopTarget.classList.remove('show')
      }
      if (!this.ticking) {
        requestAnimationFrame(this.updatePosition)
        this.ticking = true
      }
    }
  }

  updatePosition() {
    this.ticking = false

    // actioncontainer
    console.log('distance', distance)
    if (document.documentElement.scrollTop > distance) {
      this.containerActionsTarget.classList.add('stayFixed')
      this.containerActionsTarget.parentElement.style.height = `${actionsHeight}px`
      this.containerActionsTarget.style.transform = `translateY(${
        document.documentElement.scrollTop - distance
      }px)`
    } else {
      this.containerActionsTarget.classList.remove('stayFixed')
      this.containerActionsTarget.parentElement.style.height = ''
      this.containerActionsTarget.style.transform = ``
    }
  }
  scrollToTop(e) {
    e.target.blur()
    window.scrollTo({
      top: 0,
      behavior: 'smooth',
    })
  }

  selectTab(tabIndex) {
    this.deselectTabs()
    const tabs = Array.from(this.element.querySelectorAll('.btn--tab'))
    const tabsContent = Array.from(this.element.querySelectorAll('.tab-content'))
    if (tabs.length > 0 && tabsContent.length > 0) {
      this.activateTabs(tabIndex, tabs, tabsContent, this)
    }
  }

  deselectTabs() {
    const tabs = this.element.querySelectorAll('.btn--tab')
    const tabsContent = this.element.querySelectorAll('.tab-content')

    tabs.forEach(function (element) {
      element.classList.remove('active')
    })
    tabsContent.forEach(function (element) {
      element.classList.remove('active')
    })
  }

  activateTabs(tabIndex, tabs, tabsContent) {
    const activeTabs = tabs.filter((tab) => Number(tab.dataset.index) === tabIndex)
    const activeTabsContent = tabsContent.filter((tab) => Number(tab.dataset.index) === tabIndex)
    activeTabs.forEach(function (tab) {
      tab.classList.add('active')
    })
    activeTabsContent.forEach(function (tab) {
      tab.classList.add('active')
    })
    tabs.forEach(function (tab) {
      tab.addEventListener('click', function () {
        this.urlParams = new URLSearchParams(window.location.search)
        this.urlParams.set('tabIndex', tab.dataset.index)
        const targetUrl = `${window.location.pathname}?${this.urlParams}`
        detailScrollY = document.documentElement.scrollTop
        visit(targetUrl)
      })
    })
  }

  onSelectTab(e, index, tabs, tabsContent) {
    tabs.forEach(function (element) {
      element.classList.remove('active')
    })
    tabsContent.forEach(function (element) {
      element.classList.remove('active')
    })
    e.classList.add('active')
    tabsContent[index].classList.add('active')
  }

  onMapLayerChange(e) {
    const layerTypes = e.params.mapLayerTypes
    if (e.target.checked) {
      layerTypes.map((type) => this.mapLayers[type].layer.addTo(this.map))
    } else {
      layerTypes.map((type) => this.map.removeLayer(this.mapLayers[type].layer))
    }
  }
  cancelInformatieToevoegen(e) {
    const form = e.target.closest('form')
    // form.find(input["type=file"]).value=null
    form.reset()
    e.target.closest('details').open = false
  }
}
