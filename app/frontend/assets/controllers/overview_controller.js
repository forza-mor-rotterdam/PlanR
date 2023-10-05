import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  connect() {}

  navigate(e) {
    if (!e.target.closest('a')) {
      Turbo.visit(e.params.targeturl)
    }
  }

  navigateNext(e) {
    e.target
      .closest('.pagination')
      .querySelector('[checked]')
      .closest('li')
      .nextElementSibling.querySelector('input')
      .click()
  }
  navigatePrevious(e) {
    e.target
      .closest('.pagination')
      .querySelector('[checked]')
      .closest('li')
      .previousElementSibling.querySelector('input')
      .click()
  }
  openModal() {
    const modal = this.element.querySelector('.modal')
    const modalBackdrop = this.element.querySelector('.modal-backdrop')

    modal.classList.add('show')
    modalBackdrop.classList.add('show')
    document.body.classList.add('show-modal')
  }

  closeModal() {
    const modal = this.element.querySelector('.modal')
    const modalBackdrop = this.element.querySelector('.modal-backdrop')
    modal.classList.remove('show')
    modalBackdrop.classList.remove('show')
    document.body.classList.remove('show-modal')
  }
}
