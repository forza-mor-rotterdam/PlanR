import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['modal', 'turboActionModal', 'modalSluiten']

  connect() {
    console.log(`Connect: ${this.identifier}`)
  }
  openModal(event) {
    event.preventDefault()
    const modal = this.modalTarget
    const modalBackdrop = document.querySelector('.modal-backdrop')
    this.turboActionModalTarget.setAttribute('src', event.params.action)
    this.turboActionModalTarget.addEventListener('turbo:frame-load', (event) => {
      if (event.target.children.length) {
        modal.classList.add('show')
        modalBackdrop.classList.add('show')
        document.body.classList.add('show-modal')
      }
    })

    this.lastFocussedItem = event.target.closest('button')
    setTimeout(function () {
      const closeButton = modal.querySelectorAll('.btn-close')[0]
      if (closeButton) {
        closeButton.focus()
      }
    }, 1000)
  }
  closeModal() {
    const modalBackdrop = document.querySelector('.modal-backdrop')
    if (this.hasmodalTarget) {
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
      this.turboActionModalTarget.innerHTML = ''
    }
    window.removeEventListener('mousemove', this.getRelativeCoordinates, true)
  }
  modalSluitenTargetConnected() {
    this.closeModal()
  }
}
