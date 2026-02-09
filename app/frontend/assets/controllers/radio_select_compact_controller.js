import { Controller } from '@hotwired/stimulus'
export default class extends Controller {
  static targets = ['selectedLabel']

  onClickOutsideHandler(e) {
    const controllerSelector = '[data-controller="radio-select-compact"]'
    const options = e.target.closest('ul.options')
    const isThis = e.target.closest(controllerSelector) === this.element
    const isThisOptions = options?.closest(controllerSelector) === this.element

    if (isThis && !isThisOptions) {
      this.element.classList.toggle('focus')
    } else if (isThis && isThisOptions) {
      this.element.classList.remove('focus')
    } else if (!isThis) {
      this.element.classList.remove('focus')
    }
  }
  onChangeHandler(e) {
    this.selectedLabelTarget.textContent = e.target.closest('li').querySelector('label').textContent
  }
}
