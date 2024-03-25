import { Controller } from '@hotwired/stimulus'
import { visit } from '@hotwired/turbo'
export default class extends Controller {
  navigate(e) {
    if (!e.target.closest('a')) {
      visit(e.params.targeturl)
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
