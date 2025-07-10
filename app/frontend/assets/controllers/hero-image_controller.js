import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['img']

  connect() {
    const raw = this.element.dataset.heroImagePaths
    let images

    try {
      images = JSON.parse(raw)
    } catch (e) {
      console.error('Ongeldige afbeeldingslijst:', raw)
      return
    }

    if (!Array.isArray(images) || images.length === 0) return

    const randomImage = images[Math.floor(Math.random() * images.length)]

    this.imgTarget.addEventListener('load', () => {
      this.imgTarget.classList.remove('hide')
    })

    this.imgTarget.src = randomImage
  }
}
