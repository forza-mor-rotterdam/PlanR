import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static outlets = ['modal-image-slider']
  static values = {
    data: String,
  }
  static targets = ['thumb', 'thumbContainer', 'image', 'imageSliderContainer']
  initialize() {
    this.selectedCls = 'selected'
    this.bijlagen = JSON.parse(this.dataValue)
  }

  connect() {
    this._onResize = this._onResize.bind(this)
    window.addEventListener('resize', this._onResize)

    this._onResize()
  }

  disconnect() {
    window.removeEventListener('resize', this._onResize)
  }

  _onResize() {
    this.updateSlider()
  }

  modalImageSliderOutletConnected() {
    this.modalImageSliderOutlet.init(this)
  }
  thumbTargetConnected() {
    this.thumbTarget.classList.add(this.selectedCls)
  }
  selectThumbHandler(e) {
    const selectedThumb = e.target.closest('li')
    this.updateSlider(selectedThumb.dataset.imageUuid)
    this.lastViewedImage = selectedThumb.dataset.imageUuid
  }
  onScrollSliderHandler() {
    this.updateSlider(
      Math.floor(
        this.imageSliderContainerTarget.scrollLeft / this.imageSliderContainerTarget.offsetWidth
      )
    )
  }
  updateSlider(imageUuid) {
    const imageId = imageUuid || this.lastViewedImage
    this.thumbTargets.map((elem) =>
      elem.classList[imageId === elem.dataset.imageUuid ? 'add' : 'remove'](this.selectedCls)
    )
    const selectedThumb = this.thumbTargets.find((elem) =>
      elem.classList.contains(this.selectedCls)
    )
    const index = this.thumbTargets.indexOf(selectedThumb)
    this.imageSliderContainerTarget.scrollTo({
      left: Number(index) * this.imageSliderContainerTarget.offsetWidth,
      top: 0,
    })
    if (imageId) {
      selectedThumb.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' })
    }
  }
}
