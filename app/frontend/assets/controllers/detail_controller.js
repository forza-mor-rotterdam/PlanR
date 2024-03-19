import { Controller } from '@hotwired/stimulus'
import { visit } from '@hotwired/turbo'
import L from 'leaflet'

let lastFocussedItem = null
let markerIcon,
  sliderContainerWidth,
  imageSliderWidth,
  imageSliderThumbContainer = null,
  detailScrollY = 0

export default class extends Controller {
  static values = {
    signalen: String,
    locatie: String,
  }
  static targets = [
    'selectedImage',
    'thumbList',
    'imageSliderContainer',
    'imageSliderThumbContainer',
    'turboActionModal',
    'modalAfhandelen',
    'imageSliderWidth',
  ]

  initialize() {
    let self = this
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

    this.coordinates =
      JSON.parse(this.locatieValue).geometrie &&
      JSON.parse(this.locatieValue).geometrie.coordinates.reverse()
    this.signalen =
      JSON.parse(this.signalenValue).length > 1
        ? JSON.parse(this.signalenValue).filter(
            (signaal) =>
              signaal.locaties_voor_signaal.length > 0 &&
              signaal.locaties_voor_signaal[0].geometrie &&
              signaal.locaties_voor_signaal[0].geometrie.coordinates
          )
        : []

    if (this.hasThumbListTarget) {
      const element = this.thumbListTarget.getElementsByTagName('li')[0]
      element.classList.add('selected')
      imageSliderWidth = self.imageSliderWidthTarget
      imageSliderThumbContainer = self.imageSliderThumbContainerTarget
      sliderContainerWidth = imageSliderWidth.offsetWidth
      imageSliderThumbContainer.style.maxWidth = `${sliderContainerWidth}px`
    }
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
    }

    if (mapDiv && this.coordinates.length == 2) {
      markerIcon = L.Icon.extend({
        options: {
          iconSize: [32, 32],
          iconAnchor: [18, 18],
          popupAnchor: [0, -17],
        },
      })

      const markerMagenta = new markerIcon({
        iconUrl:
          'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBjbGlwLXJ1bGU9ImV2ZW5vZGQiIGQ9Ik0yMy43NzgzIDYuMjI0MTJDMTkuNTAwMyAxLjk0NjEzIDEyLjQ5OTkgMS45NDYxMyA4LjIyMTkzIDYuMjI0MTJDMy45NDM5MyAxMC41MDIxIDMuOTQzOTMgMTcuNTAyNSA4LjIyMTkzIDIxLjc4MDVMMTYuMDAwMSAyOS41NTg2TDIzLjc3ODMgMjEuNzgwNUMyOC4wNTYzIDE3LjUwMjUgMjguMDU2MyAxMC41MDIxIDIzLjc3ODMgNi4yMjQxMlpNMTYuMDAwMSAxOC4wMDIzQzE4LjIwOTIgMTguMDAyMyAyMC4wMDAxIDE2LjIxMTQgMjAuMDAwMSAxNC4wMDIzQzIwLjAwMDEgMTEuNzkzMiAxOC4yMDkyIDEwLjAwMjMgMTYuMDAwMSAxMC4wMDIzQzEzLjc5MSAxMC4wMDIzIDEyLjAwMDEgMTEuNzkzMiAxMi4wMDAxIDE0LjAwMjNDMTIuMDAwMSAxNi4yMTE0IDEzLjc5MSAxOC4wMDIzIDE2LjAwMDEgMTguMDAyM1oiIGZpbGw9IiNDOTM2NzUiLz4KPC9zdmc+Cg==',
      })
      const markerGreen = new markerIcon({
        iconUrl:
          'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMjAiIGhlaWdodD0iMjYiIHZpZXdCb3g9IjAgMCAyMCAyNiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KICAgIDxwYXRoIGQ9Ik0xNy42MzQ4IDMuNjEzMTVDMTYuNzA4OSAyLjQ4Mzc1IDE1LjU0MzkgMS41NzM4OCAxNC4yMjM5IDAuOTQ5MTM4QzEyLjkwMzggMC4zMjQzOTEgMTEuNDYxNiAwLjAwMDMzNTY5MyAxMC4wMDEyIDAuMDAwMzM1NjkzQzguNTQwNzIgMC4wMDAzMzU2OTMgNy4wOTg0OSAwLjMyNDM5MSA1Ljc3ODQzIDAuOTQ5MTM4QzQuNDU4MzggMS41NzM4OCAzLjI5MzQgMi40ODM3NSAyLjM2NzQ4IDMuNjEzMTVDMC44Mzc1NTUgNS40Njg3MiAwLjAwMDg1NDQ5MiA3Ljc5ODc1IDAuMDAwODU0NDkyIDEwLjIwMzdDMC4wMDA4NTQ0OTIgMTIuNjA4NyAwLjgzNzU1NSAxNC45Mzg3IDIuMzY3NDggMTYuNzk0M0wxMC4wMDEyIDI2LjAwMDVMMTcuNjM2IDE2Ljc5NDNDMTkuMTY1MSAxNC45MzgzIDIwLjAwMTIgMTIuNjA4MyAyMC4wMDEgMTAuMjAzNUMyMC4wMDA4IDcuNzk4NzIgMTkuMTY0MyA1LjQ2ODg2IDE3LjYzNDggMy42MTMxNVpNMTAgMTMuOTk5MUM5LjExMDA0IDEzLjk5OTEgOC4yNDAwNCAxMy43MzUyIDcuNTAwMDUgMTMuMjQwN0M2Ljc2MDA2IDEyLjc0NjMgNi4xODMzMSAxMi4wNDM1IDUuODQyNzMgMTEuMjIxM0M1LjUwMjE1IDEwLjM5OSA1LjQxMzAzIDkuNDk0MjggNS41ODY2NiA4LjYyMTRDNS43NjAyOSA3Ljc0ODUyIDYuMTg4ODUgNi45NDY3MyA2LjgxODE3IDYuMzE3NDFDNy40NDc0OCA1LjY4ODEgOC4yNDkyNyA1LjI1OTU0IDkuMTIyMTUgNS4wODU5MUM5Ljk5NTAzIDQuOTEyMjggMTAuODk5OCA1LjAwMTM5IDExLjcyMiA1LjM0MTk4QzEyLjU0NDMgNS42ODI1NiAxMy4yNDcgNi4yNTkzMSAxMy43NDE1IDYuOTk5M0MxNC4yMzU5IDcuNzM5MjkgMTQuNDk5OCA4LjYwOTI5IDE0LjQ5OTggOS40OTkyN0MxNC40OTk4IDEwLjY5MjggMTQuMDI1OCAxMS44Mzc1IDEzLjE4MTkgMTIuNjgxNUMxMi4zMzgxIDEzLjUyNTYgMTEuMTkzNiAxMy45OTk5IDEwIDE0LjAwMDJWMTMuOTk5MVoiIGZpbGw9IiMwMDgxMUYiLz4KPC9zdmc+Cg==',
      })

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
      this.map = L.map('incidentMap').setView(this.coordinates, 18)
      L.tileLayer(url, config).addTo(this.map)

      for (let i = 0; i < this.signalen.length; i++) {
        const marker = new L.Marker(
          this.signalen[i].locaties_voor_signaal[0].geometrie.coordinates.reverse(),
          { icon: markerMagenta }
        )
        marker.addTo(this.map)
        let popupContent = `<div></div><div class="container__content"><p>${this.signalen[i].bron_signaal_id}</p></div>`
        marker.bindPopup(popupContent)
      }
      const bounds = new L.LatLngBounds(
        this.signalen
          .map((signaal) => signaal.locaties_voor_signaal[0].geometrie.coordinates)
          .concat([this.coordinates])
      )
      this.map.fitBounds(bounds)
      new L.Marker(this.coordinates, { icon: markerGreen }).addTo(this.map)
    }

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        this.closeModal()
      }
    })
    if (this.hasThumbListTarget) {
      const resizeObserver = new ResizeObserver(() => {
        sliderContainerWidth = imageSliderWidth.offsetWidth
        imageSliderThumbContainer.style.maxWidth = `${sliderContainerWidth}px`
      })
      resizeObserver.observe(imageSliderWidth)
    }
  }

  connect() {
    document.documentElement.scrollTop = detailScrollY

    this.urlParams = new URLSearchParams(window.location.search)
    this.tabIndex = Number(this.urlParams.get('tabIndex'))
    this.selectTab(this.tabIndex || 1)
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
    if (e.target.checked) {
      this.mapLayers[e.params.mapLayerType].layer.addTo(this.map)
    } else {
      this.map.removeLayer(this.mapLayers[e.params.mapLayerType].layer)
    }
  }
  openModal(event) {
    event.preventDefault()
    lastFocussedItem = event.target.closest('button')
    const modal = this.modalAfhandelenTarget
    const modalBackdrop = document.querySelector('.modal-backdrop')
    this.turboActionModalTarget.setAttribute('src', event.params.action)
    modal.classList.add('show')
    modalBackdrop.classList.add('show')
    document.body.classList.add('show-modal')
    setTimeout(function () {
      modal.querySelectorAll('.btn-close')[0].focus()
    }, 1000)
  }

  closeModal() {
    const modalBackdrop = document.querySelector('.modal-backdrop')
    this.modalAfhandelenTarget.classList.remove('show')
    modalBackdrop.classList.remove('show')
    document.body.classList.remove('show-modal')
    if (lastFocussedItem) {
      lastFocussedItem.focus()
    }
    if (this.hasTurboActionModalTarget) {
      this.turboActionModalTarget.innerHTML = ''
    }
  }

  onScrollSlider() {
    this.highlightThumb(
      Math.floor(
        this.imageSliderContainerTarget.scrollLeft / this.imageSliderContainerTarget.offsetWidth
      )
    )
  }

  selectImage(e) {
    this.imageSliderContainerTarget.scrollTo({
      left: (Number(e.params.imageIndex) - 1) * this.imageSliderContainerTarget.offsetWidth,
      top: 0,
    })
    this.deselectThumbs(e.target.closest('ul'))
    e.target.closest('li').classList.add('selected')
  }

  highlightThumb(index) {
    this.deselectThumbs(this.thumbListTarget)
    const thumb = this.thumbListTarget.getElementsByTagName('li')[index]
    thumb.classList.add('selected')
    const thumbWidth = thumb.offsetWidth
    const offsetNum = thumbWidth * index
    const maxScroll = this.thumbListTarget.offsetWidth - sliderContainerWidth

    const newLeft =
      offsetNum - sliderContainerWidth / 2 > 0
        ? offsetNum - sliderContainerWidth / 3 < maxScroll
          ? offsetNum - sliderContainerWidth / 3
          : maxScroll
        : 0
    this.thumbListTarget.style.left = `-${newLeft}px`
  }

  deselectThumbs(list) {
    for (const item of list.querySelectorAll('li')) {
      item.classList.remove('selected')
    }
  }

  cancelInformatieToevoegen(e) {
    const form = e.target.closest('form')
    // form.find(input["type=file"]).value=null
    form.reset()
    e.target.closest('details').open = false
  }
}
