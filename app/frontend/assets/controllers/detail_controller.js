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
    mercurePublicUrl: String,
    mercureSubscriberToken: String,
    mercureSubscriptions: String,
    gebruiker: String,
  }
  static targets = [
    'selectedImage',
    'thumbList',
    'imageSliderContainer',
    'imageSliderThumbContainer',
    'turboActionModal',
    'modalAfhandelen',
    'imageSliderWidth',
    'gebruikersActiviteit',
  ]

  initialize() {
    let self = this
    self.gebruiker = self.hasGebruikerValue ? JSON.parse(self.gebruikerValue) : {}

    this.lastEventId = null
    this.mercureSubscriptions = []
    if (this.hasThumbListTarget) {
      const element = this.thumbListTarget.getElementsByTagName('li')[0]
      element.classList.add('selected')
      imageSliderWidth = self.imageSliderWidthTarget
      imageSliderThumbContainer = self.imageSliderThumbContainerTarget
      sliderContainerWidth = imageSliderWidth.offsetWidth
      imageSliderThumbContainer.style.maxWidth = `${sliderContainerWidth}px`
    }
    if (this.hasMercureSubscriptionsValue) {
      console.log(JSON.parse(this.mercureSubscriptionsValue))
      this.mercureSubscriptions = JSON.parse(this.mercureSubscriptionsValue)
      this.initMessages()
    }
    if (this.hasGebruikersActiviteitTarget) {
      this.gebruikersActiviteitTarget.style.display = 'none'
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

    const resizeObserver = new ResizeObserver(() => {
      sliderContainerWidth = imageSliderWidth.offsetWidth
      imageSliderThumbContainer.style.maxWidth = `${sliderContainerWidth}px`
    })
    resizeObserver.observe(imageSliderWidth)
  }
  isValidHttpUrl(string) {
    let url

    try {
      url = new URL(string)
    } catch (_) {
      return false
    }

    return url.protocol === 'http:' || url.protocol === 'https:'
  }
  initMessages() {
    let self = this
    if (self.hasMercurePublicUrlValue && self.isValidHttpUrl(self.mercurePublicUrlValue)) {
      const url = new URL(self.mercurePublicUrlValue)
      url.searchParams.append('topic', window.location.pathname)
      if (self.lastEventId) {
        url.searchParams.append('lastEventId', self.lastEventId)
      }
      if (self.hasMercureSubscriberTokenValue) {
        console.log(self.mercureSubscriberTokenValue)
        url.searchParams.append('authorization', self.mercureSubscriberTokenValue)
      }
      self.eventSource = new EventSource(url)
      self.eventSource.onmessage = (e) => self.onMessage(e)
      self.eventSource.onerror = (e) => self.onMessageError(e)
      self.updateMessagesInterval = setInterval(() => self.updateGebruikerActiviteit(), 1000)
    }
  }
  onMessage(e) {
    this.lastEventId = e.lastEventId
    let data = JSON.parse(e.data)
    console.log('mercure message', data)
    this.mercureSubscriptions = data
  }
  // unused for now
  async getSubscriptions() {
    const url = `${this.mercurePublicUrlValue}/subscriptions`

    try {
      const response = await fetch(`${url}`, {
        headers: {
          Authorization: `Bearer ${this.mercureSubscriberTokenValue}`,
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      })
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`)
      }
      return await response.json()
    } catch (error) {
      console.error('Error fetching address details:', error.message)
    }
  }
  onMessageError(e) {
    let self = this
    console.error(e)
    console.error('An error occurred while attempting to connect.')
    self.eventSource.close()
    clearInterval(self.updateMessagesInterval)
    setTimeout(() => self.initMessages(), 5000)
  }
  updateGebruikerActiviteit() {
    const self = this
    const currentDate = new Date()
    const tsOutdated = parseInt(currentDate.getTime() / 1000) - 60 * 60 * 2
    if (this.hasGebruikersActiviteitTarget) {
      let gebruikersLijstElem = this.gebruikersActiviteitTarget.querySelector('ul')
      gebruikersLijstElem.innerHTML = ''
      const subscriptions = this.mercureSubscriptions.filter(
        (sub) => self.gebruiker.email != sub.gebruiker.email && sub.timestamp > tsOutdated
      )
      if (subscriptions.length > 0) {
        this.gebruikersActiviteitTarget.style.display = 'block'
        for (let i = 0; i < subscriptions.length; i++) {
          const subscription = subscriptions[i]
          let liElem = document.createElement('li')
          const timeLeft = parseInt(parseInt(currentDate.getTime())) - subscription.timestamp * 1000
          let min = Math.floor(timeLeft / 1000 / 60 + 60) % 60
          let hours = Math.floor(timeLeft / 1000 / 60 / 60)
          let minVerbal = min > 0 ? `${min} ${min > 1 ? 'minuten' : 'minuut'}` : `< minuut`
          let hoursVerbal = hours > 0 ? `${hours} uur en ` : ``
          liElem.textContent = `${subscription.gebruiker.naam}: ${hoursVerbal}${minVerbal} geleden`
          gebruikersLijstElem.appendChild(liElem)
        }
      } else {
        this.gebruikersActiviteitTarget.style.display = 'none'
      }
    }
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
