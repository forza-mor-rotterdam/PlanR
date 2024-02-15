import { Controller } from '@hotwired/stimulus'
export default class extends Controller {
  static targets = ['filterOverview', 'filterButton', 'foldoutStateField']

  connect() {
    let self = this
    self.containerSelector = '.container__multiselect'
    self.showClass = 'show'

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
  toggleFilterElements(e) {
    let self = this
    e.stopImmediatePropagation()

    self.foldoutStateFieldTarget.value = ''
    self.filterButtonTargets.map((elem) => {
      const elemContainer = elem.closest(self.containerSelector)
      if (elem == e.target) {
        self.foldoutStateFieldTarget.value = e.target.dataset.foldoutName
        elemContainer.classList[
          elemContainer.classList.contains(self.showClass) ? 'remove' : 'add'
        ](self.showClass)
      } else {
        elemContainer.classList.remove(self.showClass)
      }
    })
  }
}
