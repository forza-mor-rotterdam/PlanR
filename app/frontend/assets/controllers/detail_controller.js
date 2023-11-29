import { Controller } from '@hotwired/stimulus'

let lastFocussedItem = null
let markerIcon,
  markerGreen = null

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
    'turboActionModal',
    'modalAfhandelen',
  ]

  initialize() {
    if (this.hasThumbListTarget) {
      this.thumbListTarget.getElementsByTagName('li')[0].classList.add('selected')
    }

    const incidentXValue = this.incidentXValue
    const incidentYValue = this.incidentYValue
    const mapDiv = document.getElementById('incidentMap')

    if (mapDiv && incidentXValue && incidentYValue) {
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

      const url =
        'https://service.pdok.nl/brt/achtergrondkaart/wmts/v2_0/{layerName}/{crs}/{z}/{x}/{y}.{format}'
      const config = {
        crs: 'EPSG:3857',
        format: 'png',
        name: 'standaard',
        layerName: 'standaard',
        type: 'wmts',
        minZoom: 6,
        maxZoom: 19,
        tileSize: 256,
        attribution: '',
      }
      const incidentCoordinates = [
        parseFloat(this.incidentXValue.replace(/,/g, '.')),
        parseFloat(this.incidentYValue.replace(/,/g, '.')),
      ]
      const map = L.map('incidentMap').setView(incidentCoordinates, 16)
      L.tileLayer(url, config).addTo(map)
      const marker = L.marker(incidentCoordinates, { icon: markerGreen }).addTo(map)
    }

    document.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        this.closeModal()
      }
    })
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
    this.thumbListTarget.getElementsByTagName('li')[index].classList.add('selected')
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
