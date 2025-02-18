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
  modalImageSliderOutletConnected() {
    this.modalImageSliderOutlet.init(this)
  }
  thumbTargetConnected() {
    this.thumbTarget.classList.add(this.selectedCls)
  }
  selectThumbHandler(e) {
    const selectedThumb = e.target.closest('li')
    this.updateSlider(selectedThumb.dataset.imageUuid)
  }
  onScrollSliderHandler() {
    this.updateSlider(
      Math.floor(
        this.imageSliderContainerTarget.scrollLeft / this.imageSliderContainerTarget.offsetWidth
      )
    )
  }
  updateSlider(imageUuid) {
    this.thumbTargets.map((elem) =>
      elem.classList[imageUuid === elem.dataset.imageUuid ? 'add' : 'remove'](this.selectedCls)
    )
    const selectedThumb = this.thumbTargets.find((elem) =>
      elem.classList.contains(this.selectedCls)
    )
    const index = this.thumbTargets.indexOf(selectedThumb)
    this.imageSliderContainerTarget.scrollTo({
      left: Number(index) * this.imageSliderContainerTarget.offsetWidth,
      top: 0,
    })
    selectedThumb.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'center' })
  }
}
