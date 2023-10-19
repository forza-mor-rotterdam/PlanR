import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  navigate(e) {
    if (!e.target.closest('a')) {
      // eslint-disable-next-line no-undef
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
}
