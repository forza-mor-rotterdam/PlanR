import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static values = {
    initialImageUuid: String,
  }
  static targets = ['image', 'nav', 'next', 'previous', 'counter', 'label', 'subLabel']

  initialize() {
    this.selectedCls = 'selected'
    this.imageUuid = this.initialImageUuidValue
  }
  disconnect() {
    const imageUuid = this.imageUuids[this.imageIndex]
    this.imageSliderController.updateSlider(imageUuid)
  }
  init(imageSliderController) {
    this.imageSliderController = imageSliderController
    this.imageUuids = this.imageSliderController.bijlagen.map((bijlage) => bijlage.uuid)
    this.imageIndex = this.imageUuids.indexOf(this.imageUuid)
    this.setNavState()
    this.imageTarget.addEventListener('mousemove', (e) => this.getRelativeCoordinates(e), true)
  }
  imageClickToggleHandler() {
    this.element.classList.toggle('fullSize')
    if (this.element.classList.contains('fullSize')) {
      this.imageTarget.style.backgroundPosition = '50% 50%'
    }
  }
  nextHandler() {
    this.updateImage(1)
  }
  previousHandler() {
    this.updateImage(-1)
  }
  bijlage() {
    return this.imageSliderController.bijlagen.find(
      (bijlage) => bijlage.uuid === this.imageUuids[this.imageIndex]
    )
  }
  updateImage(extraIndex) {
    if (
      this.imageIndex + extraIndex >= this.imageUuids.length ||
      this.imageIndex + extraIndex < 0
    ) {
      return
    }
    this.imageIndex = this.imageIndex + extraIndex

    this.setNavState()

    this.imageTarget.style.backgroundImage = `url(/core${this.bijlage().afbeelding_relative_url})`
  }
  setNavState() {
    const bijlage = this.bijlage()
    this.nextTarget.classList[this.imageIndex >= this.imageUuids.length - 1 ? 'add' : 'remove'](
      'inactive'
    )
    this.previousTarget.classList[this.imageIndex <= 0 ? 'add' : 'remove']('inactive')

    this.counterTarget.textContent = `Foto ${this.imageIndex + 1} van ${this.imageUuids.length}`
    this.labelTarget.textContent = bijlage.label
    if (bijlage.bron_signaal_id) {
      this.subLabelTarget.textContent = `${bijlage.bron_id} - ${bijlage.bron_signaal_id}`
    }
  }

  getRelativeCoordinates(e) {
    if (this.element.classList.contains('fullSize')) {
      const rect = this.imageTarget.getBoundingClientRect()
      this.imageTarget.style.backgroundPosition = `
        ${((e.clientX - rect.left) * 100) / this.imageTarget.offsetWidth}%
        ${((e.clientY - rect.top) * 100) / this.imageTarget.offsetHeight}%
        `
    } else {
      this.imageTarget.style.backgroundPosition = '50% 50%'
    }
  }
}
