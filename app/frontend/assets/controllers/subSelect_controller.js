import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static targets = ['groupCheckbox', 'subCheckbox', 'selectedCount']

  initialize() {
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
  checkboxChangeHandler(e) {
    this.subCheckboxTargets.map((checkbox) => {
      checkbox.checked = this.groupCheckboxTarget.checked
    })
    this.element.closest('form').submit()
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
}
