import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['modal', 'turboActionModal', 'modalSluiten']

  connect() {}
  openModal(event) {
    event.preventDefault()
    const modal = this.modalTarget
    const modalBackdrop = document.querySelector('.modal-backdrop')
    this.turboActionModalTarget.setAttribute('src', event.params.action)
    modal.classList.add('show')
    modalBackdrop.classList.add('show')
    document.body.classList.add('show-modal')
    this.turboActionModalTarget.addEventListener('turbo:frame-load', (event) => {
      if (event.target.children.length) {
        // modal content loaded
      }
    })

    this.lastFocussedItem = event.target.closest('button')
  }
  turboActionModalTargetConnected(target) {
    this.turboActionModalTargetClone = target.cloneNode(true)
  }
  closeModal() {
    const modalBackdrop = document.querySelector('.modal-backdrop')
    if (this.hasModalTarget) {
      this.modalTarget.classList.remove('show')
    }
    if (this.hasModalImagesTarget) {
      this.modalImagesTarget.classList.remove('show')
    }
    modalBackdrop.classList.remove('show')
    document.body.classList.remove('show-modal')
    if (this.lastFocussedItem) {
      this.lastFocussedItem.focus()
    }
    if (this.hasTurboActionModalTarget) {
      this.turboActionModalTarget.replaceWith(this.turboActionModalTargetClone.cloneNode(true))
    }
    window.removeEventListener('mousemove', this.getRelativeCoordinates, true)
  }
  modalSluitenTargetConnected() {
    this.closeModal()
  }
}
