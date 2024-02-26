import { Controller } from '@hotwired/stimulus'
import L from 'leaflet'

let lastFocussedItem = null
let markerIcon,
  markerMagenta,
  sliderContainerWidth,
  self,
  imageSliderWidth,
  imageSliderThumbContainer = null,
  detailScrollY = 0

export default class extends Controller {
  static values = {
    incidentX: String,
    incidentY: String,
    areaList: String,
    currentDistrict: String,
    signalenObject: String,
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

    this.signaalCoords = Array.from(JSON.parse(this.signalenObjectValue)).reduce(function (
      _filtered,
      signaal
    ) {
      console.log('>>> ', signaal.locaties_voor_signaal[0])
      console.log('>>> >>> ', signaal.signaal_data.adressen[0]) //  oude meldingen
      // const lat = signaal.locaties_voor_signaal[0]
      //   ? signaal.locaties_voor_signaal[0].geometrie.coordinates[1]
      //   : signaal.signaal_data.adressen.geometrie.coordinates[1]
      // const long = signaal.locaties_voor_signaal[0]
      //   ? signaal.locaties_voor_signaal[0].geometrie.coordinates[0]
      //   : signaal.signaal_data.adressen.geometrie.coordinates[0]
      // console.log('lat', signaal.locaties_voor_signaal)
      // if (lat != undefined && long != undefined) {
      //   _filtered.push([lat, long])
      // }
      return _filtered
    }, [])

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
    console.log('incidentXValue', this.incidentXValue)
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
        parseFloat(this.signaalCoords[0][0]),
        parseFloat(this.signaalCoords[0][1]),
      ]
      this.map = L.map('incidentMap').setView(incidentCoordinates, 18)
      L.tileLayer(url, config).addTo(this.map)

      for (let i = 0; i < this.signaalCoords.length; i++) {
        const lat = parseFloat(this.signaalCoords[i][0])
        const long = parseFloat(this.signaalCoords[i][1])
        new L.Marker([lat, long], { icon: markerMagenta }).addTo(this.map)
      }

      const bounds = new L.LatLngBounds(this.signaalCoords)
      this.map.fitBounds(bounds)
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
        // eslint-disable-next-line no-undef
        Turbo.visit(targetUrl)
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
