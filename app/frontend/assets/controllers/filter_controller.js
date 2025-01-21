import { Controller } from '@hotwired/stimulus'

let targetElementInView = null
let focusElement = null
export default class extends Controller {
  static targets = [
    'filterOverview',
    'filterButton',
    'foldoutStateField',
    'containerSearch',
    'searchProfielContext',
    'toggleSearchProfileContainer',
    'toggleSearchProfielContext',
  ]

  connect() {
    let self = this
    const previousFocusElement = document.getElementById(focusElement?.getAttribute('id'))
    if (previousFocusElement) {
      if (previousFocusElement.name == 'q') {
        previousFocusElement.selectionStart = previousFocusElement.selectionEnd =
          previousFocusElement.value.length
        previousFocusElement.focus()
      }
    }

    self.element[self.identifier] = self
    self.containerSelector = '.container__multiselect'
    self.showClass = 'show'
    targetElementInView = document.querySelector('.container__multiselect.show .wrapper')
    if (targetElementInView) {
      const [isInView, rect] = this.isInViewport()
      if (!isInView) {
        this.positionIntoViewport(rect)
      }
    }
    window.addEventListener('click', self.clickOutsideHandler.bind(self))
  }
  disconnect() {
    document.removeEventListener('click', this.clickOutsideHandler)
  }

  toggleSearchProfileContainerTargetConnected() {
    if (this.searchProfielContextTarget.value.length) {
      this.toggleSearchProfileContainerTarget.classList.remove('hidden')
    }
  }

  onClearSearch(e) {
    if (e.target.value.length === 0) {
      this.toggleSearchProfielContextTarget.checked = true
    }
    this.element.requestSubmit()
  }

  onChangeFilter(e) {
    focusElement = e.target
    clearTimeout(this.searchTimeout)
    if (focusElement.name == 'q') {
      return
    } else {
      this.element.requestSubmit()
    }
  }
  onToggleSearchProfielContext(e) {
    this.filterOverviewTarget.classList.toggle('disabled')
    this.onChangeFilter(e)
  }

  clickOutsideHandler(e) {
    let self = this
    if (!e.target.closest(self.containerSelector)) {
      self.foldoutStateFieldTarget.value = ''
      self.filterButtonTargets.map((elem) =>
        elem.closest(self.containerSelector).classList.remove(self.showClass)
      )
    }
  }
  addToFoldoutStates(foldout_ids) {
    let self = this
    let foldoutStates = JSON.parse(
      self.foldoutStateFieldTarget.value ? self.foldoutStateFieldTarget.value : '[]'
    )
    let d = foldoutStates.concat(foldout_ids)
    let set = new Set(d)
    d = Array.from(set)
    self.foldoutStateFieldTarget.value = JSON.stringify(d)
  }
  removeFromFoldoutStates(foldout_ids) {
    let self = this
    let foldoutStates = JSON.parse(
      self.foldoutStateFieldTarget.value ? self.foldoutStateFieldTarget.value : '[]'
    )
    foldoutStates = foldoutStates.filter((id) => !foldout_ids.includes(id))
    self.foldoutStateFieldTarget.value = JSON.stringify(foldoutStates)
  }

  isInViewport() {
    const rect = targetElementInView.getBoundingClientRect()
    const isinview =
      rect.left >= 0 && rect.right <= (window.innerWidth || document.documentElement.clientWidth)

    return [isinview, rect]
  }

  positionIntoViewport(rect) {
    const shiftX = -(rect.x + rect.width - window.innerWidth) - 20
    targetElementInView.style.transform = `translateX(${shiftX}px)`
  }

  toggleFilterElements(e) {
    let self = this
    e.stopImmediatePropagation()

    self.removeFromFoldoutStates(self.filterButtonTargets.map((f) => f.dataset.foldoutName))
    self.filterButtonTargets.map((elem) => {
      const elemContainer = elem.closest(self.containerSelector)
      if (elem == e.target) {
        self.addToFoldoutStates([e.target.dataset.foldoutName])
        elemContainer.classList[
          elemContainer.classList.contains(self.showClass) ? 'remove' : 'add'
        ](self.showClass)
        targetElementInView = elemContainer.querySelector('.wrapper')
        const [isInView, rect] = this.isInViewport()
        if (!isInView) {
          this.positionIntoViewport(rect)
        }
      } else {
        elemContainer.classList.remove(self.showClass)
      }
    })
  }
}
