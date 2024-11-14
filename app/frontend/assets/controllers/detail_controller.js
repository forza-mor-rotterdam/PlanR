import { Controller } from '@hotwired/stimulus'
import { visit } from '@hotwired/turbo'
import L from 'leaflet'

let lastFocussedItem = null
let markerIcon,
  sliderContainerWidth,
  imageSliderWidth,
  imageSliderThumbContainer = null,
  detailScrollY = 0,
  selectedImageIndex = 0,
  imagesList = null,
  fullSizeImageContainer = null,
  keyFunctions = null,
  distance = 0,
  actionsHeight = 0

export default class extends Controller {
  static values = {
    signalen: String,
    locatie: String,
    afbeeldingen: String,
    urlPrefix: String,
  }
  static targets = [
    'selectedImage',
    'selectedImageModal',
    'thumbList',
    'imageSliderContainer',
    'imageSliderThumbContainer',
    'turboActionModal',
    'modalAfhandelen',
    'modalImages',
    'imageSliderWidth',
    'navigateImagesLeft',
    'navigateImagesRight',
    'imageCounter',
    'btnToTop',
    'containerActions',
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
    if (this.locatieValue) {
      this.coordinates = JSON.parse(this.locatieValue)?.geometrie?.coordinates?.reverse()
    }

    if (this.signalenValue) {
      this.signalen =
        JSON.parse(this.signalenValue)?.filter(
          (signaal) => signaal.locaties_voor_signaal?.[0]?.geometrie?.coordinates
        ) ?? []
    }

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

    if (mapDiv && this.coordinates?.length == 2) {
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

      for (const signaal of this.signalen) {
        const coordinates = signaal.locaties_voor_signaal[0].geometrie.coordinates.reverse()
        const marker = new L.Marker(coordinates, { icon: markerMagenta })
        marker.addTo(this.map)
        const popupContent = `<div></div><div class="container__content"><p>${signaal.bron_signaal_id}</p></div>`
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
    if (this.afbeeldingenValue) {
      imagesList = JSON.parse(this.afbeeldingenValue).map(
        (bestand) => bestand.afbeelding_relative_url
      )
    }

    keyFunctions = (e) => {
      if (e.key === 'Escape') {
        this.closeModal()
      }
      if (e.key === 'ArrowLeft') {
        this.showPreviousImageInModal()
      }
      if (e.key === 'ArrowRight') {
        this.showNextImageInModal()
      }
    }

    document.addEventListener('keyup', keyFunctions)
    actionsHeight = this.containerActionsTarget.offsetHeight
    window.addEventListener(
      'scroll',
      function () {
        this.checkScrollPosition()
      }.bind(this),
      false
    )
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
      // actioncontainer
      if (document.documentElement.scrollTop > distance) {
        this.containerActionsTarget.classList.add('stayFixed')

        this.containerActionsTarget.nextElementSibling.style.marginTop = `${actionsHeight}px`
      } else {
        this.containerActionsTarget.classList.remove('stayFixed')
        this.containerActionsTarget.nextElementSibling.style.marginTop = 0
      }
    }
  }

  disconnect() {
    document.removeEventListener('keyup', keyFunctions)
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
    if (e.target.checked) {
      this.mapLayers[e.params.mapLayerType].layer.addTo(this.map)
    } else {
      this.map.removeLayer(this.mapLayers[e.params.mapLayerType].layer)
    }
  }
  openModal(event) {
    event.preventDefault()
    const modal = this.modalAfhandelenTarget
    const modalBackdrop = document.querySelector('.modal-backdrop')

    this.turboActionModalTarget.setAttribute('src', event.params.action)
    this.turboActionModalTarget.addEventListener('turbo:frame-load', (event) => {
      if (event.target.children.length) {
        modal.classList.add('show')
        modalBackdrop.classList.add('show')
        document.body.classList.add('show-modal')
      }
    })

    // lastFocussedItem = event.target.closest('button')
    // setTimeout(function () {
    //   const closeButton = modal.querySelectorAll('.btn-close')[0]
    //   if (closeButton) {
    //     closeButton.focus()
    //   }
    // }, 1000)
  }

  closeModal() {
    const modalBackdrop = document.querySelector('.modal-backdrop')
    if (this.hasModalAfhandelenTarget) {
      this.modalAfhandelenTarget.classList.remove('show')
    }
    if (this.hasModalImagesTarget) {
      this.modalImagesTarget.classList.remove('show')
    }
    modalBackdrop.classList.remove('show')
    document.body.classList.remove('show-modal')
    if (lastFocussedItem) {
      lastFocussedItem.focus()
    }
    if (this.hasTurboActionModalTarget) {
      this.turboActionModalTarget.innerHTML = ''
    }
    window.removeEventListener('mousemove', this.getRelativeCoordinates, true)
  }

  onScrollSlider() {
    this.highlightThumb(
      Math.floor(
        this.imageSliderContainerTarget.scrollLeft / this.imageSliderContainerTarget.offsetWidth
      )
    )
  }

  imageScrollInView(index) {
    this.imageSliderContainerTarget.scrollTo({
      left: Number(index) * this.imageSliderContainerTarget.offsetWidth,
      top: 0,
    })
  }

  selectImage(e) {
    this.imageScrollInView(e.params.imageIndex)
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

  showPreviousImageInModal() {
    if (selectedImageIndex > 0) {
      selectedImageIndex--
      this.showImage()
    }
  }

  showNextImageInModal() {
    if (selectedImageIndex < imagesList.length - 1) {
      selectedImageIndex++
      this.showImage()
    }
  }

  showImage() {
    this.selectedImageModalTarget.style.backgroundImage = `url('${this.urlPrefixValue}${imagesList[selectedImageIndex]}')`
    this.showHideImageNavigation()
    this.imageCounterTarget.textContent = `Foto ${selectedImageIndex + 1} van ${imagesList.length}`
    this.imageScrollInView(selectedImageIndex) //image in detailpage
    fullSizeImageContainer = this.selectedImageModalTarget
    this.showNormal()
    window.addEventListener('mousemove', this.getRelativeCoordinates, true)
    this.selectedImageModalTarget.addEventListener('click', this.showLarge)
  }

  getRelativeCoordinates(e) {
    if (fullSizeImageContainer.classList.contains('fullSize')) {
      fullSizeImageContainer.style.backgroundPosition = `
        ${(e.clientX * 100) / window.innerWidth}%
        ${(e.clientY * 100) / window.innerHeight}%
        `
    }
  }

  showLarge() {
    if (fullSizeImageContainer.classList.contains('fullSize')) {
      fullSizeImageContainer.classList.remove('fullSize')
      fullSizeImageContainer.style.backgroundPosition = '50% 50%'
      window.removeEventListener('mousemove', this.getRelativeCoordinates, true)
    } else {
      fullSizeImageContainer.classList.add('fullSize')
      window.addEventListener('mousemove', this.getRelativeCoordinates, true)
    }
  }

  showNormal() {
    fullSizeImageContainer.classList.remove('fullSize')
    fullSizeImageContainer.style.backgroundPosition = '50% 50%'
    window.removeEventListener('mousemove', this.getRelativeCoordinates, true)
  }

  showHideImageNavigation() {
    this.navigateImagesLeftTarget.classList.remove('inactive')
    this.navigateImagesRightTarget.classList.remove('inactive')
    if (selectedImageIndex === 0) {
      this.navigateImagesLeftTarget.classList.add('inactive')
    }
    if (selectedImageIndex === imagesList.length - 1) {
      this.navigateImagesRightTarget.classList.add('inactive')
    }
  }

  showImageInModal(e) {
    selectedImageIndex = e.params.imageIndex
    const modal = this.modalImagesTarget
    const modalBackdrop = document.querySelector('.modal-backdrop')
    modal.classList.add('show')
    modalBackdrop.classList.add('show')
    document.body.classList.add('show-modal')

    this.showImage()
  }
}
