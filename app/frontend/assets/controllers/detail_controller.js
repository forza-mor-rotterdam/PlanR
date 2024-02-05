import { Controller } from '@hotwired/stimulus'
import L from 'leaflet'

let lastFocussedItem = null
let markerIcon,
  markerMagenta,
  sliderContainerWidth,
  self,
  imageSliderWidth,
  imageSliderThumbContainer = null

export default class extends Controller {
  static values = {
    incidentX: String,
    incidentY: String,
    areaList: String,
    currentDistrict: String,
    incidentObject: Object,
  }
  static targets = [
    'selectedImage',
    'thumbList',
    'imageSliderContainer',
    'imageSliderThumbContainer',
    'turboActionModal',
    'modalAfhandelen',
    'imageSliderWidth',
    'tabs',
    'tabsContent',
  ]

  initialize() {
    let self = this

    if (this.hasTabsTarget && this.hasTabsContentTarget) {
      const tabs = this.tabsTarget.querySelectorAll('.btn--tab')
      const tabsContent = this.tabsContentTarget.querySelectorAll('.tab-content')
      tabs[0].classList.add('active')
      tabsContent[0].classList.add('active')
      tabs.forEach(function (e, index) {
        e.addEventListener('click', function () {
          self.onSelectTab(e, index, tabs, tabsContent)
        })
      })
    }

    if (this.hasThumbListTarget) {
      const element = this.thumbListTarget.getElementsByTagName('li')[0]
      element.classList.add('selected')
      imageSliderWidth = self.imageSliderWidthTarget
      imageSliderThumbContainer = self.imageSliderThumbContainerTarget
      sliderContainerWidth = imageSliderWidth.offsetWidth
      imageSliderThumbContainer.style.maxWidth = `${sliderContainerWidth}px`
    }

    const incidentXValue = this.incidentXValue
    const incidentYValue = this.incidentYValue
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

    if (mapDiv && incidentXValue && incidentYValue) {
      markerIcon = L.Icon.extend({
        options: {
          iconSize: [32, 32],
          iconAnchor: [18, 18],
          popupAnchor: [0, -17],
        },
      })

      markerMagenta = new markerIcon({
        iconUrl:
          'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBjbGlwLXJ1bGU9ImV2ZW5vZGQiIGQ9Ik0yMy43NzgzIDYuMjI0MTJDMTkuNTAwMyAxLjk0NjEzIDEyLjQ5OTkgMS45NDYxMyA4LjIyMTkzIDYuMjI0MTJDMy45NDM5MyAxMC41MDIxIDMuOTQzOTMgMTcuNTAyNSA4LjIyMTkzIDIxLjc4MDVMMTYuMDAwMSAyOS41NTg2TDIzLjc3ODMgMjEuNzgwNUMyOC4wNTYzIDE3LjUwMjUgMjguMDU2MyAxMC41MDIxIDIzLjc3ODMgNi4yMjQxMlpNMTYuMDAwMSAxOC4wMDIzQzE4LjIwOTIgMTguMDAyMyAyMC4wMDAxIDE2LjIxMTQgMjAuMDAwMSAxNC4wMDIzQzIwLjAwMDEgMTEuNzkzMiAxOC4yMDkyIDEwLjAwMjMgMTYuMDAwMSAxMC4wMDIzQzEzLjc5MSAxMC4wMDIzIDEyLjAwMDEgMTEuNzkzMiAxMi4wMDAxIDE0LjAwMjNDMTIuMDAwMSAxNi4yMTE0IDEzLjc5MSAxOC4wMDIzIDE2LjAwMDEgMTguMDAyM1oiIGZpbGw9IiNDOTM2NzUiLz4KPC9zdmc+Cg==',
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
      const incidentCoordinates = [
        parseFloat(this.incidentXValue.replace(/,/g, '.')),
        parseFloat(this.incidentYValue.replace(/,/g, '.')),
      ]
      this.map = L.map('incidentMap').setView(incidentCoordinates, 18)
      L.tileLayer(url, config).addTo(this.map)
      L.marker(incidentCoordinates, { icon: markerMagenta }).addTo(this.map)
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
