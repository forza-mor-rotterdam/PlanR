import { Controller } from '@hotwired/stimulus'
import debounce from 'debounce'

let scrollPositionForDialog = 0

export default class extends Controller {
  static targets = [
    'filtersheet',
    'selectedChoicesCount',
    'selectedChoicesTotalCount',
    'searchProfielContext',
    'toggleSearchProfileContainer',
  ]

  initialize() {
    this.submit = debounce(this.submit.bind(this), 400)
  }

  connect() {
    this.element[this.identifier] = this
    this.updateSelectedChoicesCount()
  }

  // ===========================================================
  // Filter dialog
  // ===========================================================
  showFilters() {
    scrollPositionForDialog = window.scrollY
    document.body.style.top = `-${scrollPositionForDialog}px`
    document.body.style.position = 'fixed'
    this.filtersheetTarget.showModal()
    this.filtersheetTarget.addEventListener('click', (event) => {
      if (event.target === event.currentTarget) {
        event.stopPropagation()
        this.hideFilters()
      }
    })
  }

  hideFilters() {
    document.body.style.position = ''
    document.body.style.top = ''
    this.filtersheetTarget.close()
    window.scrollTo({ top: scrollPositionForDialog, left: 0, behavior: 'instant' })
  }

  hideFiltersAndSubmit() {
    this.hideFilters()
    this.submit()
  }

  // ===========================================================
  // Filter selection
  // ===========================================================
  onChangeFilter(e) {
    // Inside dialog: update counts only. Outside (e.g. ordering): submit.
    if (this.hasFiltersheetTarget && this.filtersheetTarget.contains(e.target)) {
      this.updateSelectedChoicesCount()
    } else {
      this.submit()
    }
  }

  removeFilter(e) {
    const { name, value } = e.params
    const input = this.element.querySelector(`input[name="${CSS.escape(name)}"][value="${CSS.escape(value)}"]`)
    if (input) {
      input.checked = false
      input.dispatchEvent(new Event('change', { bubbles: true }))
    }
    this.submit()
  }

  removeAllFilters() {
    this.filterInputs.forEach((input) => {
      input.checked = false
    })
    this.updateSelectedChoicesCount()
  }

  selectAll(e) {
    const checkList = Array.from(
      e.target.closest('details.filter').querySelectorAll(
        'input[type="checkbox"]:not([data-sub-select-target="groupCheckbox"])'
      )
    )
    const doCheck = e.params.filterType === 'all'
    checkList.forEach((el) => {
      el.checked = doCheck
    })
    this.updateSelectedChoicesCount()
  }

  // ===========================================================
  // Count helpers
  // ===========================================================
  get filterInputs() {
    if (!this.hasFiltersheetTarget) return []
    return Array.from(
      this.filtersheetTarget.querySelectorAll(
        'input[type="checkbox"]:not([data-sub-select-target="groupCheckbox"])'
      )
    ).filter((input) => input.name && input.name !== 'search_with_profiel_context')
  }

  updateSelectedChoicesCount() {
    this.selectedChoicesCountTargets.forEach((elem) => {
      let container = elem.closest('details.filter')
      if (!container) {
        container = this.hasFiltersheetTarget ? this.filtersheetTarget : this.element
      }
      const count = Array.from(
        container.querySelectorAll(
          'input[type="checkbox"]:checked:not([data-sub-select-target="groupCheckbox"])'
        )
      ).filter((input) => input.name && input.name !== 'search_with_profiel_context').length
      elem.textContent = `${count}`
    })
    if (this.hasSelectedChoicesTotalCountTarget) {
      const total = this.filterInputs.filter((i) => i.checked).length
      this.selectedChoicesTotalCountTarget.textContent = `${total}`
    }
  }

  // ===========================================================
  // Backward-compat stubs used by subSelect controller
  // ===========================================================
  addToFoldoutStates() {}
  removeFromFoldoutStates() {}

  // ===========================================================
  // Search
  // ===========================================================
  toggleSearchProfileContainerTargetConnected() {
    if (this.searchProfielContextTarget.value.length) {
      this.toggleSearchProfileContainerTarget.classList.remove('hidden')
    }
  }

  onClearSearch() {
    if (!this.searchProfielContextTarget.value.length) {
      this.submit()
    }
  }

  onToggleSearchProfielContext() {
    this.submit()
  }

  // ===========================================================
  // Submit
  // ===========================================================
  submit() {
    this.element.requestSubmit()
  }
}
