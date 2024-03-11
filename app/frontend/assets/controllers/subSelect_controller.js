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
  checkboxChangeHandler(e) {
    this.subCheckboxTargets.map((checkbox) => {
      checkbox.checked = this.groupCheckboxTarget.checked
    })
    this.element.closest('form').submit()
  }
}
