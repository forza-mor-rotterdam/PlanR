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
    'filterButton',
    'filteredCount',
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
    // Submit form first, then close dialog after submission completes
    this.submit()
    // Give form submission time to process before closing
    setTimeout(() => {
      this.hideFilters()
    }, 100)
  }

  // ===========================================================
  // Filter selection
  // ===========================================================
  onChangeFilter(e) {
    // Inside dialog: update counts only. Outside (e.g. ordering): submit.
    if (this.hasFiltersheetTarget && this.filtersheetTarget.contains(e.target)) {
      this.updateSelectedChoicesCount()
      this.updateFilteredCount()
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
    this.updateFilteredCount()
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
    this.updateFilteredCount()
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

  async updateFilteredCount() {
    if (!this.hasFilteredCountTarget) return
    
    // Create FormData with current filter selections
    const formData = new FormData(this.element)
    
    try {
      // Build URL with filter_count action parameter
      const url = new URL(window.location)
      url.searchParams.set('action', 'filter_count')
      
      console.log('Fetching filter count from:', url.toString())
      console.log('Form data:', Object.fromEntries(formData))
      
      const response = await fetch(url.toString(), {
        method: 'POST',
        body: formData,
        headers: {
          'X-Requested-With': 'XMLHttpRequest',
        }
      })
      
      if (response.ok) {
        const data = await response.json()
        console.log('Filter count response:', data)
        if (data.count !== undefined) {
          this.filteredCountTarget.textContent = data.count
          console.log('Updated button text to:', data.count)
        }
      } else {
        const text = await response.text()
        console.warn('Error response from filter count endpoint:', response.status, text)
      }
    } catch (error) {
      console.error('Error fetching filtered count:', error)
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
