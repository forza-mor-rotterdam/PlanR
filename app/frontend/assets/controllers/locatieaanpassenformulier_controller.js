import { Controller } from '@hotwired/stimulus'
import { capitalize } from 'lodash'

let form = null
let inputList = null
let markerGreen, markerBlue, markerIcon
let initialGeometry = {}
const defaultErrorMessage = 'Vul a.u.b. dit veld in.'

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
    'buurtnaam',
    'wijknaam',
    'geometrie',
    'internalText',
    'map',
  ]

  connect() {
    form = document.querySelector('#afhandelForm')
    inputList = document.querySelectorAll('.js-validation textarea')
    const locatie = JSON.parse(this.locatieValue)
    initialGeometry = locatie.geometrie
    console.log('initialGeometry', initialGeometry)
    this.initializeMap(locatie)
    this.updateFormFields(locatie)

    for (const element of inputList) {
      const input = element
      const error = input.closest('.form-row').getElementsByClassName('invalid-text')[0]
      input.addEventListener('input', () => {
        if (input.validity.valid) {
          input.closest('.form-row').classList.remove('is-invalid')
          error.textContent = ''
        } else {
          error.textContent = defaultErrorMessage
          input.closest('.form-row').classList.add('is-invalid')
        }
      })
    }

    form.addEventListener('submit', (event) => {
      console.log('form submit')
      const coordinatesValid = !this.checkSameCoordinates()

      if (!coordinatesValid) {
        window.alert('Het is niet toegestaan om de locatie aan te passen met dezelfde coordinaten.')
        event.preventDefault()
      }
    })
  }

  initializeMap(locatie) {
    var url =
      'https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0/{layerName}/{crs}/{z}/{x}/{y}.{format}'
    var config = {
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

    const map = L.map(this.mapTarget).setView([0, 0], 17) // 17 is the zoom level
    if (map) {
      markerIcon = L.Icon.extend({
        options: {
          iconSize: [26, 26],
          iconAnchor: [13, 13],
          popupAnchor: [0, -17],
        },
      })

      markerGreen = new markerIcon({
        iconUrl:
          'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAASTSURBVHgBrZZNbBtFFMf/O7vrr42xGylKQ9PU4YDaHCDtiVtSIVFEL+WQcGvFqSAkEAghDlXrqL1xQEJCqDkgDiAhRXwKSotEUziAxAEipEQgRY2BBEdKGtuJY6/t3Rne26w/Gnmdz2c97+7Mzvu99+bNzGrYraRTSWjyEjRtFArD1JLyezJbqj6CEj8incnsxpy24xtvDxxBVLxGhkmR3PF9qAlc+ye901udwddPDELiLprR7VYWUMPTuPH3QtALYnuDUkrzHLqybyjLIEz8QNOTIns7gxlKojywuW9oE66pu9obx7v9YILBDE2n04I8vXZAaBOeMF71otkG3+6JFr5y/LGKKeZxeJLDUvVxTGYf0H0j72KbE6KiibOdrKQS/Zi++Clyb/0BdTWDz8dvem0dJImjoUs+SwsEQ1cXO0F/v3wLo6mnkIw84rU9f/Icfrv8bSe4Rr+RtuBGJQMGXU4EWXj33NUGsFWORBL48MI7QDD6ib6+PhPbwRMTE9rQ0JDe3d1tUtdA0PgLJ58JtD3cO4QO4IFaraYzo870/qiSMTc3J9bW1nR0kLy9HtjXLhOtsrq6apRKJTE2NqY1wPzQ39+vxeNxHVItBg2eWZ4LNPzVX98H9pHNf5mVyWTE1NQUGmB60CqVir6xsaHDUYHWX/z6zbZR5+wCXr9zHYHiqCU0i6sRsXezsrKy1ViUvwaNz+QXcXryOXzpR8dOTGd+wZnJ815fgCjk3S/QLCyt8Tc6OmrMzs5GCG7hVOwYXui5Rz1xHI4o3CucxXT+z56enk1iVKjNaaxjIQTvKip8313HmvMJDkseODfDP5cXu7q6JD9SkB7HA4+MjEgfLGlbdfHN2sc0L//hoOLS3L639AHVjywWi5KilfWu+jpGNpvlRtfT++U8vsu9fCA4j72deykUCjnRaLTGdlOplKSIPXjrhPPOEia1wuFwnLy0cCY+iPNH3oeh9WEv4qisfnv9FTGzuUAbR5FaNvz5rdI9O6Ee2jBoWxOUakELXSdPhbtYLuOnwmc4ZQl06cPY6YtFqiKyVB9TKzeM+eoyQe1IJGI7jmOTTYY68E+oVkOcdsOPOkYDLClljPbxKKmpnrSOuUOR03jUfBYhcbSRBUcto6zmkavN4E7uFhYrBdM0iVkrU2+JdNO/VurRPgTmg2J8fJx3FiOZTEar1WqUvIyxE2SInTHImIHmicZjlWEYGkXE86boPY7IofcYUorFYiUWhtLuWCPbLloGtwo/c/p5viO+RvlKRkN1OMPqYwnqJZnUZbAPtUnLiUTCLhQKth+pi5YPgU6HgheFZVmSjEkWAkrXdR26dUm9q2+U1aZnmyq4TMVZ5vmlAq1QFddoj5at0HYR10WgOeemr17ENPeGbds6GRdk13OQ2iS1ueRkVdf1KhVmjU4jdsapB7BbsNbiAGdFp+Wgc5rz+bze4piiHUnR5qD8VDq0VjlCvpdUN9L/at2zbH0ObcE54ggdnzznVl17e3stWoZchBE/M14Btvuk3bOwEd+Ql34+VOpXqlYvI/61UXS7iWg/0m7cnlL6P5qNFK3aTp7nAAAAAElFTkSuQmCC',
      })
      markerBlue = new markerIcon({
        iconSize: [18, 18],
        iconAnchor: [9, 9],
        iconUrl:
          'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAB4AAAAeCAYAAAA7MK6iAAAACXBIWXMAAAsTAAALEwEAmpwYAAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAATESURBVHgBrVZNTGNVFL7vp9AfCB0mpAOSoRgdGUQcI8yiCYImGjXExBBYGbshcdGiKxHHhSVRdG+M0YWrccUC4qSz0EQT2RATiNHEBFKcjnYmg6BtLfa/7/qdx72vr50OU+qc5OTed9895zvn3HPOvYw1SZxzL/gt8Br4Bq8Szb8HB8F+9qAolUqdgcIIOMmbowj7vwQlg3XeNUu/5XK5wZN0Kw3AFBCDoN/pdH6HJb/8t3GTsWu7nEV3GbuZOl4b9TH2BPjKhMIGvDWqboCfA8dJ34nAApRjqmK+J0FTecY+2uDs0x/ZiRS6fGxAl7MKnkgkxvr7+5NCr0VqjRX4GYlE1Eql8r4d9KWr9wcloj0vY286by0N9vX1vWl6A6dqsOpkFSTTw11dXTG58M63zYHaKQzPP37eUp3c2tq6MDY29hfmltdqnRGqw+F4Vi7QOZ4WlIhkKB8EeUdGRoICS7kncFtb2+tyYWWDs1aIpKK7lqyiadpkQ2ARf2JdVdUB+fOXO6xlurZTnUPnaG9vr+Mu4OXlZWV4eFjr7u52YNN5+fPnP1nL9Hu6Bvh8qVTSCENiKjYD2sAueP+3FOj4sLVQS8WZ9ywHqU7P+v3+3Pj4eGl1dbVios/OziqoNaWzs1ODZQm5e6CLtUzUVCShPP/AoMbjcRWg5poJjA+lUChomUxGQ8f6VQpMX2At06gNGLpvsWpyKcz2wQ4ODszF/f19q4CmH1NYK0RS7z5TDXMsFltj1WO1gPnU1BTr6emhA+VLS0trCE2Gfk4gv0Pj7NQUuqzUHNP6+jo5owDDArfqGJlnAkej0X9g4Vdy/Qosf9LHmiYK8dJE9XtnZ+fzlZWVREdHh0HfcNLEMYEnJycNAWwg+yoLCwtX8/n8bfpHDf/6awoLjze4yhp4Snu94pKgsx0aGvoMo3F0dGTgOI16GTKAtp/BVUh1/Hg4HH4FiXbLfsnGU5y/8bXBA18Y3PPBMQ9/YvC3vzH4D/HaC5lkQ6HQNDrhsMvl6odOL8rJSZeQHZicoTruBJ9rb29/FOOl+fn5V7PZ7G1+SiIZkkXfvwQ9j4B9ON8OgXFX4DS0NTdq+SzmA7D0IsYxcGB7e/tL6DPuB4gekKG9gUDgBYA+DdmLIoLdYBdhSGClLtw6uB3shoDHMAw39FE3cwSDwYdmZmaeQud50ePxnEP4ekkIIb2TTCZje3t7Py0uLl7f3NxMAxQ2lHL4nQX/K8YCuMTE1VgtNlwUc3Nz1Fl0r9frKhaLLoTMTUZAERmjQ5nOqjcayXJd15VyuUxJw7GvjLGMfQSSdbvdWSICRXc0W6X9bOvPmsLhEMnmFCFyQmmbBCcwKQtQGgi4QsAClN4gOTwo8um0+R4hTyvM9hDQ2L3J9AJhNaDMIAKggeZSxrQCNkehlDiP7zyOIIfkzEEmjzIqoG5L6NGGHbSRx5JUVj1zh2DTY5y9jhrXoFyFXtNArBlYq8DIIi79IhKzdHh4SMaUpQPNAtuvS4qKhnKgm0vHm0yzGcbRkTiaAxehLKNWyUOaUxUY9a/LZsl8Dglw8tiJ65PO3CPZ5/N5qAzZcT44RJTU+ldlS0RKhCIz/Dg3XY7IVjMiYrSSrhmPWqFGcqcK6X9czfgLQYqNowAAAABJRU5ErkJggg==',
      })

      L.tileLayer(url, config).addTo(map)

      // Get the current location and set a marker on the map
      const locatieCoordinates = [
        locatie.geometrie.coordinates[1],
        locatie.geometrie.coordinates[0],
      ]

      const newLocation = locatieCoordinates
      const oldLocationMarker = L.marker(locatieCoordinates, { icon: markerGreen })
        .bindPopup('Oude locatie')
        .addTo(map)
      const newLocationMarker = L.marker(newLocation, { draggable: true, icon: markerBlue })
        .bindPopup('Nieuwe locatie')
        .addTo(map)

      newLocationMarker.on('dragend', async (event) => {
        const newCoordinates = event.target.getLatLng()
        // Assuming you have a variable to store the coordinates, update it here
        this.newLocationCoordinates = [newCoordinates.lat, newCoordinates.lng]
        await this.updateAddressDetails(this.newLocationCoordinates)

        // You can use this.newLocationCoordinates as needed
      })

      map.on('click', async (event) => {
        const clickedCoordinates = [event.latlng.lat, event.latlng.lng]
        newLocationMarker.setLatLng(clickedCoordinates)
        this.newLocationCoordinates = clickedCoordinates
        await this.updateAddressDetails(this.newLocationCoordinates)

        // You can use this.newLocationCoordinates as needed
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
  }

  updateFormFields(locatie) {
    // Update form fields with values from locatie
    this.constructor.targets.forEach((key) => {
      if (this[`has${capitalize(key)}Target`]) {
        if (key === 'geometrie') {
          this[`${key}Target`].value = JSON.stringify(locatie[key])
        } else {
          this[`${key}Target`].value = locatie[key]
        }
      }
    })
  }

  searchResultToLocatie(result) {
    const mapping = {
      straatnaam: 'straatnaam',
      postcode: 'postcode',
      huisnummer: 'huisnummer',
      huisletter: 'huisletter',
      huisnummertoevoeging: 'toevoeging',
      woonplaatsnaam: 'plaatsnaam',
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

  async updateAddressDetails(coordinates) {
    const pdokUrl = 'https://api.pdok.nl/bzk/locatieserver/search/v3_1/reverse'
    const query = {
      lat: coordinates[0],
      lon: coordinates[1],
      fl: [
        'straatnaam',
        'postcode',
        'huisnummer',
        'huisletter',
        'huisnummertoevoeging',
        'woonplaatsnaam',
        'wijknaam',
        'buurtnaam',
      ],
    }

    try {
      const response = await fetch(`${pdokUrl}?${new URLSearchParams(query)}`)
      if (!response.ok) {
        throw new Error(`HTTP error! Status: ${response.status}`)
      }

      const data = await response.json()
      const addressDetails = data.response.docs[0]

      // Convert the PDOK search result to a locatie object
      const locatie = this.searchResultToLocatie(addressDetails)
      locatie['geometrie'] = {
        type: 'Point',
        coordinates: [coordinates[1], coordinates[0]],
      }

      // Update your form fields or perform other actions with locatie
      this.updateFormFields(locatie)
    } catch (error) {
      console.error('Error fetching address details:', error.message)
    }
  }

  checkSameCoordinates() {
    console.log('checkValids')
    const newGeometry = JSON.parse(document.querySelector('#id_geometrie').value)
    console.log('initialGeometry', initialGeometry.coordinates)
    console.log('newGeometry', newGeometry.coordinates)
    const sameCoordinates =
      initialGeometry.coordinates[0] === newGeometry.coordinates[0] &&
      initialGeometry.coordinates[1] === newGeometry.coordinates[1]

    return sameCoordinates
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
