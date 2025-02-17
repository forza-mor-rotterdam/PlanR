import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static outlets = ['modal-image-slider', 'modal']
  static values = {
    data: String,
  }
  static targets = [
    'selectedImage',
    'selectedImageModal',
    'thumbList',
    'imageSliderThumbContainer',
    'modalImages',
    'imageSliderWidth',
    'navigateImagesLeft',
    'navigateImagesRight',
    'imageCounter',

    'thumb',
    'image',
    'imageSliderContainer',
  ]

  initialize() {
    this.selectedCls = 'selected'
    this.bijlagen = JSON.parse(this.dataValue)
  }
  modalImageSliderOutletConnected(outlet) {
    console.log('modalImageSliderOutletConnected from: ', this.identifier)
    console.log(outlet)
    this.modalImageSliderOutlet.init(this)
  }
  modalOutletConnected(outlet) {
    console.log('modal outlet')
    console.log(outlet)
  }
  connect() {
    console.log('MODAL OUTLET')
    console.log(this.hasModalImageSliderOutlet)
    console.log(this.hasModalOutlet)
    // console.log(this.modalImageSliderOutlet)
    // console.log(this.modalImageSliderOutlets)
    // console.log(JSON.parse(this.dataValue))
  }
  thumbTargetConnected() {
    this.thumbTarget.classList.add(this.selectedCls)
  }
  selectThumbHandler(e) {
    const selectedThumb = e.target.closest('li')
    this.updateSlider(selectedThumb.dataset.imageUuid)
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
  }
  showImage() {
    // this.selectedImageModalTarget.style.backgroundImage = `url('${this.urlPrefixValue}${imagesList[selectedImageIndex]}')`
    // this.showHideImageNavigation()
    // this.imageCounterTarget.textContent = `Foto ${selectedImageIndex + 1} van ${imagesList.length}`
    // this.imageScrollInView(selectedImageIndex) //image in detailpage
    // fullSizeImageContainer = this.selectedImageModalTarget
    // this.showNormal()
    // window.addEventListener('mousemove', this.getRelativeCoordinates, true)
    // this.selectedImageModalTarget.addEventListener('click', this.showLarge)
  }
}
