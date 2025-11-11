import { Controller } from '@hotwired/stimulus'

export default class extends Controller {
  static values = {
    dateObject: String,
    rowQuerySelector: String,
  }
  initialize() {
    this.rowQuerySelector = this.rowQuerySelectorValue || 'li'
    console.log(this.rowQuerySelector)
  }

  selectAll(e) {
    e.preventDefault()
    let checkList
    if (!e.target.closest('.form-row')) {
      checkList = Array.from(
        this.element.querySelectorAll(
          `.form-row ${this.rowQuerySelector}:not([style*="display:none"]):not([style*="display: none"]`
        )
      )
    } else {
      checkList = Array.from(
        e.target
          .closest('.form-row')
          .querySelectorAll(
            `${this.rowQuerySelector}:not([style*="display:none"]):not([style*="display: none"]`
          )
      )
    }
    console.log('checklist length', checkList.length)
    const doCheck = e.params.filterType === 'all'
    checkList.forEach((element) => {
      element.querySelector('input[type="checkbox"]').checked = doCheck
    })
    if (e.target.closest('.form-row').querySelector('.label i')) {
      const checkedItems = e.target.closest('.form-row').querySelectorAll('input:checked')
      e.target.closest('.form-row').querySelector('.label i').textContent = checkedItems.length
    }
  }
}
