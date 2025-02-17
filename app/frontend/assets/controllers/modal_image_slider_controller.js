import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static values = {
    data: String,
    initialImageUuid: String,
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
  ]

  initialize() {
    this.selectedCls = 'selected'
  }
  connect() {
    console.log(this.identifier)
  }

  init(imageSliderController) {
    this.imageSliderController = imageSliderController
    console.log('this.imageSliderController.bijlagen.length')
    console.log(this.imageSliderController.bijlagen.length)
  }

  getRelativeCoordinates() {}

  showLarge() {}

  showNormal() {}
}
