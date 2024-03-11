import { Controller } from '@hotwired/stimulus'
export default class extends Controller {
  static targets = ['filterOverview', 'filterButton', 'foldoutStateField', 'containerSearch']

  connect() {
    let self = this
    self.element[self.identifier] = self
    self.containerSelector = '.container__multiselect'
    self.showClass = 'show'

    if (this.hasContainerSearchTarget) {
      const searchInput = this.containerSearchTarget.querySelector('input[type=search]')
      searchInput.addEventListener('search', function () {
        self.element.requestSubmit()
      })
      searchInput.addEventListener('blur', function () {
        self.element.requestSubmit()
      })
    }

    window.addEventListener('click', self.clickOutsideHandler.bind(self))
  }
  disconnect() {
    document.removeEventListener('click', this.clickOutsideHandler)
  }
  onChangeFilter(e) {
    this.element.requestSubmit()
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
      } else {
        elemContainer.classList.remove(self.showClass)
      }
    })
  }
}
