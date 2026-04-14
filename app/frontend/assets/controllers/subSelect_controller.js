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
    }`
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
    self.filterController = document.querySelector('[data-controller="filter"]')?.filter
  }

  checkboxChangeHandler() {
    this.subCheckboxTargets.map((checkbox) => {
      checkbox.checked = this.groupCheckboxTarget.checked
    })
    const selected = this.subCheckboxTargets.filter((c) => c.checked).length
    this.selectedCountTarget.textContent = `${selected}`
    this.groupCheckboxTarget.classList.toggle('half-checked', selected > 0 && selected < this.subCheckboxTargets.length)
    this.filterController?.updateSelectedChoicesCount?.()
    this.filterController?.updateFilteredCount?.()
  }

  toggleGroupElements(e) {
    // Foldout state tracking removed — native <details> handles open/closed state.
  }
}
