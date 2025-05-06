import { Controller } from '@hotwired/stimulus'
import debounce from 'debounce'

export default class extends Controller {
  static targets = ['groupCheckbox', 'subCheckbox', 'selectedCount']

  initialize() {
    this.submit = debounce(this.submit.bind(this), 400)
    const checkboxCount = this.subCheckboxTargets.length
    const checkboxSelectedCount = this.subCheckboxTargets.filter(
      (checkbox) => checkbox.checked
    ).length
    this.selectedCountTarget.textContent = `${
      this.subCheckboxTargets.filter((checkbox) => checkbox.checked).length
    }/${this.subCheckboxTargets.length}`
    if (checkboxCount == checkboxSelectedCount) {
      this.groupCheckboxTarget.checked = true
    }
    if (checkboxCount != checkboxSelectedCount && checkboxSelectedCount != 0) {
      this.groupCheckboxTarget.classList.add('half-checked')
    }
  }
  connect() {
    let self = this
    self.element[self.identifier] = self
    self.filterController = document.querySelector('[data-controller="filter"]').filter
  }
  checkboxChangeHandler() {
    this.subCheckboxTargets.map((checkbox) => {
      checkbox.checked = this.groupCheckboxTarget.checked
    })
    this.submit()
  }
  toggleGroupElements(e) {
    let self = this
    e.stopImmediatePropagation()
    if (self.filterController && e.target.hasAttribute('open')) {
      self.filterController.addToFoldoutStates([e.params.foldoutId])
    } else if (self.filterController) {
      self.filterController.removeFromFoldoutStates([e.params.foldoutId])
    }
  }
  submit() {
    this.element.closest('form').submit()
  }
}
