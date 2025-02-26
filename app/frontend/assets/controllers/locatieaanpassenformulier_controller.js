import { Controller } from '@hotwired/stimulus'
import { capitalize } from 'lodash'
import L from 'leaflet'

// eslint-disable-next-line no-unused-vars
let inputList,
  savedScrollPosition,
  scrollbarWidth = null
// eslint-disable-next-line no-unused-vars
let initialGeometry = {}
let markerBlue, markerMagenta, markerIcon

export default class extends Controller {
  static values = {
    formIsSubmitted: Boolean,
    locatie: String,
  }
  static targets = [
    'plaatsnaam',
    'straatnaam',
    'huisnummer',
    'huisletter',
    'toevoeging',
    'postcode',
    'wijknaam',
    'buurtnaam',
    'geometrie',
    'internalText',
    'map',
    'adresResultList',
    'submitButton',
    'address',
    'currentAddressDistance',
    'searchable',
  ]

  connect() {
    let self = this
    inputList = document.querySelectorAll('.js-validation textarea')
    const locatie = JSON.parse(this.locatieValue)
    this.address = JSON.parse(this.locatieValue)
    this.initial = true
    this.geometrie = {
      type: 'Point',
      coordinates: [locatie.geometrie.coordinates[0], locatie.geometrie.coordinates[1]],
    }
    this.currentHash = this.getHash(
      `${this.getAddressString(locatie)}${this.geometrie.coordinates[0]}${
        this.geometrie.coordinates[1]
      }`
    )
    initialGeometry = locatie.geometrie
    this.initializeMap(locatie)
    this.updateFormFields(locatie)

    self.element.addEventListener('submit', (event) => {
      if (!this.dataHasChanged()) {
        event.preventDefault()
      } else {
        document.body.classList.remove('show-modal')
      }
    })

    this.updateAddressDetails([locatie.geometrie.coordinates[1], locatie.geometrie.coordinates[0]])
  }

  initializeMap(locatie) {
    const url =
      'https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0/{layerName}/{crs}/{z}/{x}/{y}.{format}'
    const config = {
      crs: 'EPSG:3857',
      format: 'png',
      name: 'standaard',
      layerName: 'standaard',
      type: 'wmts',
      minZoom: 11,
      maxZoom: 22,
      tileSize: 256,
      attribution: '',
    }

    const map = L.map(this.mapTarget, { scrollWheelZoom: false }).setView([0, 0], 17)
    if (map) {
      markerIcon = L.Icon.extend({
        options: {
          iconSize: [32, 32],
          iconAnchor: [18, 18],
          popupAnchor: [0, -17],
        },
      })

      markerBlue = new markerIcon({
        iconSize: [18, 18],
        iconAnchor: [9, 9],
        iconUrl:
          'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAATESURBVHgBrVZNTGNVFL7vp9AfCB0mpAOSoRgdGUQcI8yiCYImGjXExBBYGbshcdGiKxHHhSVRdG+M0YWrccUC4qSz0EQT2RATiNHEBFKcjnYmg6BtLfa/7/qdx72vr50OU+qc5OTed9895zvn3HPOvYw1SZxzL/gt8Br4Bq8Szb8HB8F+9qAolUqdgcIIOMmbowj7vwQlg3XeNUu/5XK5wZN0Kw3AFBCDoN/pdH6HJb/8t3GTsWu7nEV3GbuZOl4b9TH2BPjKhMIGvDWqboCfA8dJ34nAApRjqmK+J0FTecY+2uDs0x/ZiRS6fGxAl7MKnkgkxvr7+5NCr0VqjRX4GYlE1Eql8r4d9KWr9wcloj0vY286by0N9vX1vWl6A6dqsOpkFSTTw11dXTG58M63zYHaKQzPP37eUp3c2tq6MDY29hfmltdqnRGqw+F4Vi7QOZ4WlIhkKB8EeUdGRoICS7kncFtb2+tyYWWDs1aIpKK7lqyiadpkQ2ARf2JdVdUB+fOXO6xlurZTnUPnaG9vr+Mu4OXlZWV4eFjr7u52YNN5+fPnP1nL9Hu6Bvh8qVTSCENiKjYD2sAueP+3FOj4sLVQS8WZ9ywHqU7P+v3+3Pj4eGl1dbVios/OziqoNaWzs1ODZQm5e6CLtUzUVCShPP/AoMbjcRWg5poJjA+lUChomUxGQ8f6VQpMX2At06gNGLpvsWpyKcz2wQ4ODszF/f19q4CmH1NYK0RS7z5TDXMsFltj1WO1gPnU1BTr6emhA+VLS0trCE2Gfk4gv0Pj7NQUuqzUHNP6+jo5owDDArfqGJlnAkej0X9g4Vdy/Qosf9LHmiYK8dJE9XtnZ+fzlZWVREdHh0HfcNLEMYEnJycNAWwg+yoLCwtX8/n8bfpHDf/6awoLjze4yhp4Snu94pKgsx0aGvoMo3F0dGTgOI16GTKAtp/BVUh1/Hg4HH4FiXbLfsnGU5y/8bXBA18Y3PPBMQ9/YvC3vzH4D/HaC5lkQ6HQNDrhsMvl6odOL8rJSZeQHZicoTruBJ9rb29/FOOl+fn5V7PZ7G1+SiIZkkXfvwQ9j4B9ON8OgXFX4DS0NTdq+SzmA7D0IsYxcGB7e/tL6DPuB4gekKG9gUDgBYA+DdmLIoLdYBdhSGClLtw6uB3shoDHMAw39FE3cwSDwYdmZmaeQud50ePxnEP4ekkIIb2TTCZje3t7Py0uLl7f3NxMAxQ2lHL4nQX/K8YCuMTE1VgtNlwUc3Nz1Fl0r9frKhaLLoTMTUZAERmjQ5nOqjcayXJd15VyuUxJw7GvjLGMfQSSdbvdWSICRXc0W6X9bOvPmsLhEMnmFCFyQmmbBCcwKQtQGgi4QsAClN4gOTwo8um0+R4hTyvM9hDQ2L3J9AJhNaDMIAKggeZSxrQCNkehlDiP7zyOIIfkzEEmjzIqoG5L6NGGHbSRx5JUVj1zh2DTY5y9jhrXoFyFXtNArBlYq8DIIi79IhKzdHh4SMaUpQPNAtuvS4qKhnKgm0vHm0yzGcbRkTiaAxehLKNWyUOaUxUY9a/LZsl8Dglw8tiJ65PO3CPZ5/N5qAzZcT44RJTU+ldlS0RKhCIz/Dg3XY7IVjMiYrSSrhmPWqFGcqcK6X9czfgLQYqNowAAAABJRU5ErkJggg==',
      })
      markerMagenta = new markerIcon({
        iconUrl:
          'data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iMzIiIGhlaWdodD0iMzIiIHZpZXdCb3g9IjAgMCAzMiAzMiIgZmlsbD0ibm9uZSIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj4KPHBhdGggZmlsbC1ydWxlPSJldmVub2RkIiBjbGlwLXJ1bGU9ImV2ZW5vZGQiIGQ9Ik0yMy43NzgzIDYuMjI0MTJDMTkuNTAwMyAxLjk0NjEzIDEyLjQ5OTkgMS45NDYxMyA4LjIyMTkzIDYuMjI0MTJDMy45NDM5MyAxMC41MDIxIDMuOTQzOTMgMTcuNTAyNSA4LjIyMTkzIDIxLjc4MDVMMTYuMDAwMSAyOS41NTg2TDIzLjc3ODMgMjEuNzgwNUMyOC4wNTYzIDE3LjUwMjUgMjguMDU2MyAxMC41MDIxIDIzLjc3ODMgNi4yMjQxMlpNMTYuMDAwMSAxOC4wMDIzQzE4LjIwOTIgMTguMDAyMyAyMC4wMDAxIDE2LjIxMTQgMjAuMDAwMSAxNC4wMDIzQzIwLjAwMDEgMTEuNzkzMiAxOC4yMDkyIDEwLjAwMjMgMTYuMDAwMSAxMC4wMDIzQzEzLjc5MSAxMC4wMDIzIDEyLjAwMDEgMTEuNzkzMiAxMi4wMDAxIDE0LjAwMjNDMTIuMDAwMSAxNi4yMTE0IDEzLjc5MSAxOC4wMDIzIDE2LjAwMDEgMTguMDAyM1oiIGZpbGw9IiNDOTM2NzUiLz4KPC9zdmc+Cg==',
      })

      L.tileLayer(url, config).addTo(map)

      // Get the current location and set a marker on the map
      const locatieCoordinates = [
        locatie.geometrie.coordinates[1],
        locatie.geometrie.coordinates[0],
      ]

      const newLocation = locatieCoordinates
      const oldLocationMarker = L.marker(locatieCoordinates, {
        icon: markerMagenta,
        draggable: false,
        autoPan: false,
      })
        .bindPopup('Oude locatie')
        .addTo(map)
      const newLocationMarker = L.marker(newLocation, {
        draggable: true,
        icon: markerBlue,
      })
        .bindPopup('Nieuwe locatie')
        .addTo(map)

      newLocationMarker.on('dragend', async (event) => {
        const newCoordinates = event.target.getLatLng()
        // Assuming you have a variable to store the coordinates, update it here
        this.newLocationCoordinates = [newCoordinates.lat, newCoordinates.lng]
        await this.updateAddressDetails(this.newLocationCoordinates)

        // You can use this.newLocationCoordinates as needed
      })

      newLocationMarker.on('mouseup', () => {
        document.activeElement.blur()
      })

      map.on('click', async (event) => {
        const clickedCoordinates = [event.latlng.lat, event.latlng.lng]
        newLocationMarker.setLatLng(clickedCoordinates)
        this.newLocationCoordinates = clickedCoordinates
        await this.updateAddressDetails(this.newLocationCoordinates)
      })
      map.getContainer().addEventListener(
        'wheel',
        (e) => {
          if (e.ctrlKey) {
            e.preventDefault()
            map.scrollWheelZoom.enable()
            this.preventScrollJumps(true)
          } else {
            map.scrollWheelZoom.disable()
            this.preventScrollJumps(false)
          }
        },
        { passive: false }
      )

      // Zet scroll-zoom weer uit zodra de muis het wiel loslaat
      map.getContainer().addEventListener('mouseleave', () => {
        map.scrollWheelZoom.disable()
        this.preventScrollJumps(false)
      })

      document.addEventListener('keyup', (e) => {
        if (e.key === 'Control') {
          this.preventScrollJumps(false)
        }
      })
      document.addEventListener(
        'wheel',
        function (e) {
          if (e.ctrlKey) {
            // Als de muis niet op de kaart staat, laat browser-zoom toe
            if (!map.getContainer().contains(e.target)) {
              return // Niets blokkeren → standaard browser-zoom
            }
          }
        },
        { passive: false }
      )

      map.once('mouseover', () => {
        this.setScrollBarWidth()
      })

      map.on('mouseout', () => {
        map.scrollWheelZoom.disable()
        this.preventScrollJumps(false)
      })

      oldLocationMarker.on('mouseover mouseout', function (event) {
        if (event.type === 'mouseover') {
          this.openPopup()
        } else if (event.type === 'mouseout') {
          this.closePopup()
        }
      })

      newLocationMarker.on('mouseover mouseout', function (event) {
        if (event.type === 'mouseover') {
          this.openPopup()
        } else if (event.type === 'mouseout') {
          this.closePopup()
        }
      })
      map.setView(locatieCoordinates)
    }
    document.querySelector('#dialogGeneral').addEventListener('scroll', (e) => {
      e.preventDefault()
      if (document.activeElement != document.querySelector('.leaflet-marker-draggable')) {
        savedScrollPosition = document.querySelector('#dialogGeneral').scrollTop
      } else {
        document.querySelector('#dialogGeneral').scrollTop = savedScrollPosition
      }
    })
  }

  setScrollBarWidth() {
    const content = document.querySelector('#dialogGeneral')
    scrollbarWidth = content.offsetWidth - content.clientWidth
  }
  preventScrollJumps(enable) {
    const content = document.querySelector('#dialogGeneral')

    if (enable) {
      // Voorkom verspringen door padding toe te voegen
      content.style.overflow = 'hidden'
      content.style.paddingRight = `${scrollbarWidth}px`
    } else {
      // Herstel originele instellingen
      content.style.overflow = ''
      content.style.paddingRight = ''
    }
  }

  updateFormFields(locatie) {
    // Update form fields with values from locatie
    this.constructor.targets.forEach((key) => {
      if (this[`has${capitalize(key)}Target`]) {
        if (key === 'geometrie') {
          this[`${key}Target`].value = JSON.stringify(this[key])
        } else {
          this[`${key}Target`].value = locatie[key]
        }
      }
    })
  }

  searchResultToLocatie(result) {
    const mapping = {
      afstand: 'afstand',
      straatnaam: 'straatnaam',
      postcode: 'postcode',
      huisnummer: 'huisnummer',
      huisletter: 'huisletter',
      huisnummertoevoeging: 'toevoeging',
      woonplaatsnaam: 'plaatsnaam',
      gemeentenaam: 'gemeente',
      wijknaam: 'wijknaam',
      buurtnaam: 'buurtnaam',
    }

    const locatie = {}
    for (const pdokKey in mapping) {
      const siaKey = mapping[pdokKey]
      locatie[siaKey] = result[pdokKey] || ''
    }

    return locatie
  }
  getHash(str) {
    return str.split('').reduce((prev, curr) => ((prev << 5) - prev + curr.charCodeAt(0)) | 0, 0)
  }
  getAddressId(address) {
    return this.getHash(this.getAddressString(address))
  }
  getAddressString(address) {
    const cleanValue = (value) => value || ''
    return `${cleanValue(address.straatnaam)}_${cleanValue(address.huisnummer)}${cleanValue(
      address.huisletter
    )}${cleanValue(address.toevoeging)}${cleanValue(address.buurtnaam)}${cleanValue(
      address.wijknaam
    )}${cleanValue(address.postcode)}`
  }
  getAddressVerbose(address) {
    const cleanValue = (value) => value || ''
    return (
      `<span data-locatieaanpassenformulier-target="searchable" class="address">
      ${address.straatnaam} ${address.huisnummer}` +
      `${cleanValue(address.huisletter)} ${cleanValue(address.toevoeging)} ${cleanValue(
        address.gemeente
      )}</span>` +
      (address.current ? `<small class="active">&nbsp;(Huidig adres)</small>` : ``) +
      `<br><span data-locatieaanpassenformulier-target="searchable" class="area">${address.buurtnaam} ${address.wijknaam}</span>`
    )
  }
  searchAddressHandler(e) {
    this.addressTargets.forEach((address) => {
      address.style.display = 'none'
    })

    this.searchableTargets.forEach((elem) => {
      const re = new RegExp(e.target.value, 'gi')
      let newContent = elem.dataset.value
      if (re.test(elem.dataset.value)) {
        elem.closest('.new-address').style.display = 'list-item'
        newContent = newContent.replace(re, function (match) {
          return '<mark>' + match + '</mark>'
        })
      }
      elem.innerHTML = newContent
    })
  }
  addressSelectHandler(e) {
    Array.from(this.adresResultListTarget.querySelectorAll('.new-address')).map((elem) =>
      elem.classList.remove('selected-address')
    )
    e.target.closest('.new-address').classList.add('selected-address')
    this.updateFormFields(e.params.locatieData)
    this.address = e.params.locatieData
    this.submitButtonTarget.disabled = !this.dataHasChanged()
  }
  prepareResponseData(responseData) {
    let self = this
    const currentAddressId = this.getAddressId(JSON.parse(this.locatieValue))
    return responseData.map((address) => {
      address = self.searchResultToLocatie(address)
      address.id = this.getAddressId(address)
      address.current = address.id === currentAddressId
      address.isFirst = this.getAddressId(responseData[0]) === address.id
      address.selected = !self.initial ? address.isFirst : address.current

      // eslint-disable-next-line no-useless-escape
      address.stringified = JSON.stringify(address).replace(/[\/\(\)\']/g, '&apos;')
      address.verbose = this.getAddressVerbose(address)
      if (address.selected) {
        this.updateFormFields(address)
        this.address = address
      }
      if (self.initial && address.isFirst) {
        this.currentAddressDistanceTarget.textContent = Math.round(address.afstand)
      }

      return address
    })
  }
  updateAdresResultList(addressList) {
    console.log('addressList', addressList)
    console.log('adresResultListTarget', this.adresResultListTarget)
    const currentAddressClass = (address) => (address.current ? ' current-address ' : '')
    const checked = (address) => (address.selected ? 'checked' : '')
    this.adresResultListTarget.innerHTML = ''
    addressList.map((address) => {
      let resultHTML =
        `<li data-locatieaanpassenformulier-target="address" class="new-address ${currentAddressClass(
          address
        )}">` +
        `<input ${checked(address)} type="radio" class="form-radio-input" tabindex="0" id="id_${
          address.id
        }" value="${
          address.id
        }" name="nieuwe_adres" data-action="locatieaanpassenformulier#addressSelectHandler" data-locatieaanpassenformulier-locatie-data-param='${
          address.stringified
        }' />` +
        `<label for="id_${address.id}">` +
        `<span>${address.verbose}</span>` +
        `<small class="distance">` +
        `${Math.round(address.afstand)} meter vanaf huidige locatie` +
        `</small>` +
        `</label>` +
        `</li>`
      let div = document.createElement('div')
      div.innerHTML = resultHTML.trim()
      this.adresResultListTarget.append(div.firstChild)
    })
    this.searchableTargets.forEach((elem) => {
      elem.dataset.value = elem.textContent
    })
  }
  async updateAddressDetails(coordinates) {
    const pdokUrl = 'https://api.pdok.nl/bzk/locatieserver/search/v3_1/reverse'
    const query = {
      lat: coordinates[0],
      lon: coordinates[1],
      rows: 50,
      fl: [
        'id',
        'straatnaam',
        'postcode',
        'huisnummer',
        'huisletter',
        'huisnummertoevoeging',
        'woonplaatsnaam',
        'gemeentenaam',
        'wijknaam',
        'buurtnaam',
        'afstand',
      ],
    }

    try {
      const response = await fetch(`${pdokUrl}?${new URLSearchParams(query)}`)
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`)
      }
      this.geometrie = {
        type: 'Point',
        coordinates: [coordinates[1], coordinates[0]],
      }
      const data = await response.json()
      this.updateAdresResultList(this.prepareResponseData(data.response.docs))
      this.submitButtonTarget.disabled = !this.dataHasChanged()
      this.initial = false
    } catch (error) {
      console.error('Error fetching address details:', error.message)
    }
  }

  dataHasChanged() {
    this.newHash = this.getHash(
      `${this.getAddressString(this.address)}${this.geometrie.coordinates[0]}${
        this.geometrie.coordinates[1]
      }`
    )
    return this.newHash != this.currentHash
  }

  cancelHandle() {
    this.element.dispatchEvent(
      new CustomEvent('cancelHandle', {
        detail: JSON.parse(this.parentContextValue),
        bubbles: true,
      })
    )
  }
}
